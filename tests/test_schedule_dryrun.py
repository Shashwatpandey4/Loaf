import json
from datetime import datetime

from src.fullstack_kb_answerer import FullStackKBAnswerer
from knowledge.recipes import get_all_recipes


def test_schedule_meal_plan_dry_run():
    kb = FullStackKBAnswerer()

    # Build a simple plan using first 7 recipes from knowledge
    recipes = kb.get_available_recipes()
    plan_recipes = recipes[:7]
    plan = {f"day_{i+1}": plan_recipes[i].name for i in range(7)}
    recipes_map = {r.name: r for r in recipes}

    start_date = datetime(2025, 11, 21)

    events = kb.schedule_meal_plan(
        plan=plan,
        recipes_map=recipes_map,
        start_date=start_date,
        time_str="18:00",
        dry_run=True,
    )

    # Expect 7 event payloads
    assert isinstance(events, list)
    assert len(events) == 7

    # Each event should have expected keys and ISO datetimes
    for i, ev in enumerate(events):
        assert ev.get("summary") == f"Meal: {plan[f'day_{i+1}']}"
        assert "start" in ev and "dateTime" in ev["start"]
        assert "end" in ev and "dateTime" in ev["end"]
        # Try parsing start datetime
        _ = datetime.fromisoformat(ev["start"]["dateTime"])  # will raise if invalid
