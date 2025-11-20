"""Agentic meal-prep runner.

Generates a 7-day meal plan using `FullStackKBAnswerer` and optionally
 schedules the meals in Google Calendar using `calendar_agent`.

Usage (Windows cmd):
  python scripts\agentic_meal_prep.py --diet vegetarian --condition none --start 2025-11-21 --time 18:00 --schedule

If `--schedule` is passed the script will prompt for OAuth on first run and
 create events in the user's primary calendar.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
import sys
from typing import List

from src.fullstack_kb_answerer import FullStackKBAnswerer
from src.models.contracts import Recipe

try:
    from calendar_agent.google_calendar import get_credentials, create_event_from_details
except Exception:
    get_credentials = None
    create_event_from_details = None


def parse_args():
    p = argparse.ArgumentParser(description="Generate a 7-day meal plan and optionally schedule it")
    p.add_argument("--diet", choices=["vegetarian", "non-vegetarian"], default="non-vegetarian")
    p.add_argument("--condition", choices=["none", "diabetes", "blood_pressure"], default="none")
    p.add_argument("--start", help="Start date (YYYY-MM-DD). Defaults to today")
    p.add_argument("--time", default="18:00", help="Time of day for events (HH:MM) default 18:00")
    p.add_argument("--schedule", action="store_true", help="Create Google Calendar events for the plan")
    p.add_argument("--dry-run", action="store_true", help="Build event payloads but do not call Google APIs")
    p.add_argument("--credentials", default="credentials.json", help="Path to Google OAuth client secrets JSON")
    p.add_argument("--token", default="token.json", help="Path to store token JSON")
    return p.parse_args()


def filter_recipes(recipes: List[Recipe], diet: str, condition: str) -> List[Recipe]:
    out = []
    banned_meat = ["chicken", "fish", "egg", "beef", "pork"]

    for r in recipes:
        name_lower = r.name.lower()
        tags_lower = [t.lower() for t in r.tags]
        # Diet filtering
        if diet == "vegetarian":
            if any(m in name_lower for m in banned_meat):
                continue
            if any(m in ",".join(tags_lower) for m in banned_meat):
                continue

        # Medical condition heuristics (prefer structured nutrition if available)
        nutr = getattr(r, "nutrition_info", None) or {}

        def _parse_amount(val: str) -> float | None:
            """Return amount in grams if parsable from a string like '12 g' or '12g' or numeric."""
            if val is None:
                return None
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip().lower()
            # find first number
            import re

            m = re.search(r"([0-9]*\.?[0-9]+)", s)
            if not m:
                return None
            num = float(m.group(1))
            if "mg" in s:
                return num / 1000.0
            if "g" in s and "kg" not in s:
                return num
            if "kg" in s:
                return num * 1000.0
            if "cup" in s:
                # rough conversions depend on substance; assume sugar/fat ~ 200g per cup
                return num * 200.0
            if "tbsp" in s or "tablespoon" in s:
                # 1 tablespoon sugar ~= 12.5 g
                return num * 12.5
            if "tsp" in s or "teaspoon" in s:
                return num * 4.2
            # fallback: assume grams
            return num

        def get_nutrient_grams(nutr_dict: dict, keys: List[str]) -> float | None:
            for k in keys:
                if k in nutr_dict and nutr_dict[k] is not None:
                    return _parse_amount(nutr_dict[k])
            return None

        if condition == "diabetes":
            sugar_keys = ["sugarContent", "sugar", "sugars"]
            sugar_g = get_nutrient_grams(nutr, sugar_keys)
            if sugar_g is not None:
                # convert grams to tablespoons (~12.5 g per tbsp)
                tbsp = sugar_g / 12.5
                if tbsp > 3:
                    continue
            else:
                # fallback: avoid recipes that mention sugar or sweet
                if "sugar" in name_lower or any("sugar" in ing.name.lower() for ing in r.ingredients):
                    continue
                if any("sweet" in t for t in tags_lower):
                    continue

        if condition == "blood_pressure":
            fat_keys = ["fatContent", "fat", "totalFat"]
            fat_g = get_nutrient_grams(nutr, fat_keys)
            if fat_g is not None:
                # treat >20g as high fat per serving
                if fat_g > 20.0:
                    continue
            else:
                # fallback: avoid recipes with tags indicating high fat
                if any("high fat" in t or "fat" in t for t in tags_lower):
                    continue
                if any(ing.name.lower() in ["butter", "ghee"] for ing in r.ingredients):
                    continue

        out.append(r)

    return out


def build_plan(recipes: List[Recipe]) -> dict:
    plan = {}
    for i in range(7):
        if i < len(recipes):
            plan[f"day_{i+1}"] = recipes[i].name
        else:
            plan[f"day_{i+1}"] = "No recipe available"
    return plan


def schedule_plan(plan: dict, recipes_map: dict, start_date: datetime, time_str: str, creds_path: str, token_path: str):
    if get_credentials is None:
        raise RuntimeError("Calendar integration not available. Install calendar dependencies.")

    creds = get_credentials(client_secrets_file=creds_path, token_file=token_path)

    hour, minute = map(int, time_str.split(":"))

    created_links = []

    for i in range(7):
        day_key = f"day_{i+1}"
        recipe_name = plan.get(day_key)
        recipe = recipes_map.get(recipe_name)

        start_dt = datetime.fromisoformat(start_date.isoformat() if isinstance(start_date, datetime) else start_date)
        start_dt = start_dt.replace(hour=hour, minute=minute)
        start_dt = start_dt + timedelta(days=i)

        description = ""
        duration = 60
        if recipe:
            description = recipe.description
            try:
                duration = int(recipe.prep_time.split()[0]) + int(recipe.cook_time.split()[0])
            except Exception:
                duration = 60

        created = create_event_from_details(
            credentials=creds,
            title=f"Meal: {recipe_name}",
            start_dt=start_dt,
            duration_minutes=duration,
            description=description,
            timezone="UTC",
        )

        created_links.append(created.get("htmlLink"))

    return created_links


def main():
    args = parse_args()

    kb = FullStackKBAnswerer()
    recipes = kb.get_available_recipes()

    filtered = filter_recipes(recipes, args.diet, args.condition)

    if not filtered:
        print("No recipes found for the specified diet/condition combination.")
        sys.exit(2)

    plan_recipes = filtered[:7]
    plan = build_plan(plan_recipes)

    recipes_map = {r.name: r for r in filtered}

    print("7-day meal plan (JSON):")
    print(json.dumps(plan, indent=2))

    if args.schedule or args.dry_run:
        start_date = datetime.fromisoformat(args.start) if args.start else datetime.now()
        print("Scheduling events in Google Calendar... (dry-run)" if args.dry_run else "Scheduling events in Google Calendar...")
        kb = FullStackKBAnswerer()
        result = kb.schedule_meal_plan(
            plan=plan,
            recipes_map=recipes_map,
            start_date=start_date,
            time_str=args.time,
            credentials_path=args.credentials,
            token_path=args.token,
            timezone="UTC",
            dry_run=args.dry_run,
        )

        if args.dry_run:
            print("Event payloads (dry-run):")
            print(json.dumps(result, indent=2))
        else:
            print("Created events:")
            for link in result:
                print(link)


if __name__ == "__main__":
    main()
