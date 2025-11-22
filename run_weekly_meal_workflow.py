#!/usr/bin/env python3
"""
Clickless weekly meal workflow:
1. Read meal plan JSON
2. Generate grocery list
3. Schedule calendar events (meals + grocery order)
4. Optionally trigger payment
"""

import json
import random
from datetime import datetime, timedelta
import requests
import stripe
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

from src.fullstack_kb_answerer import FullStackKBAnswerer

from src.fullstack_kb_answerer import FullStackKBAnswerer
from calendar_agent.google_calendar import get_credentials, create_event_from_details

# Optional: import payment trigger if you want automatic Stripe payment
import requests
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv('STRIPE_API_KEY')
exa_api_key = os.getenv('EXA_API_KEY')
os.environ["EXA_API_KEY"] = exa_api_key

# --- CONFIGURATION ---
MEAL_PLAN_FILE = Path("meal_plan_nested.json")
GROCERY_LIST_FILE = Path("output_examples/grocery_list.json")
TIMEZONE = "America/Los_Angeles"
CALENDAR_ID = "primary"

STANDARD_GROCERY_UNITS = {
        "pasta": ("1 package (16 oz / 454 g)", 1.29),
        "mixed mushrooms": ("1 package (8 oz / 227 g)", 3.99),
        "heavy cream": ("1 pint (473 ml)", 2.49),
        "parmesan cheese": ("1 block (8 oz / 227 g)", 4.99),
        "garlic": ("1 bulb", 0.89),
        "butter": ("1 stick (113 g)", 1.50),
        "fresh thyme": ("1 bunch", 2.99),
        "salt": ("1 container (700 g–1 kg)", 1.29),
        "black pepper": ("1 container (50 g)", 3.49),
        "kalamata olives": ("1 jar (200 g)", 4.99),
        "manzanilla olives": ("1 jar (200 g)", 4.99),
        "naan breads": ("1 pack (2 pieces)", 2.50),
        "mozzarella cheese": ("1 ball (8 oz / 227 g)", 3.99),
        "extra virgin olive oil": ("1 bottle (500 mL)", 7.99),
        "arugula": ("1 bag (5 oz / 140 g)", 3.49),
        "balsamic vinegar": ("1 bottle (500 mL)", 5.99),
        "milk": ("1 gallon (3.78 L)", 3.49),
        "coconut milk": ("1 can (400 mL)", 1.99),
        "pods cardamom": ("1 jar (10 pods)", 3.50),
        "ground cinnamon": ("1 jar (40 g)", 2.99),
        "sugar": ("1 bag (4 lb / 1.8 kg)", 2.49),
        "pomegranate seeds": ("1 container (100 g)", 4.99),
        "bay leaves": ("1 jar (10 leaves)", 2.99),
        "broccoli florets": ("1 bag (12 oz / 340 g)", 2.99),
        "carrot": ("1 lb / 4–5 carrots", 1.29),
        "flour": ("1 bag (5 lb / 2.27 kg)", 2.99),
        "half-and-half": ("1 pint (473 mL)", 2.49),
        "chicken broth": ("1 carton (32 oz / 946 mL)", 2.49),
        "nutmeg": ("1 jar (30 g)", 3.99),
        "onion": ("1 lb / 2–3 onions", 1.29),
        "sharp and cheddar cheese": ("1 block (8 oz / 227 g)", 4.99),
        "sourdough bread boules": ("1 loaf (7 inches)", 4.99),
        "coconut milk (ml)": ("1 can (200 ml)", 1.49),
        "egg yolks": ("1 dozen eggs", 3.49),
        "full milk (ml)": ("1 liter", 1.29),
        "honey": ("1 bottle (500 g)", 5.49),
        "lime": ("1 unit", 0.79),
        "pineapple": ("1 whole (2–3 lb)", 3.99),
        "tapioca": ("1 package (100 g)", 2.49),
        "vanilla pod": ("1 pod", 1.99),
        "roasted beets": ("1 bunch (3–4 medium beets)", 4.99),
        "chickpeas": ("1 can (15 oz / 425 g)", 1.79),
        "ground cumin": ("1 jar (40 g)", 2.58),
        "juice of lemon": ("1 lemon", 0.79),
        "tahini sesame seed paste": ("1 jar (454 g / 16 oz)", 5.49)
    }
# --- HELPER FUNCTIONS ---
def generate_grocery_list(meal_plan_file: Path, kb: FullStackKBAnswerer):
    """Generate a grocery list JSON from meal plan, using KB first, then web fallback."""
    with open(meal_plan_file, "r") as f:
        meal_plan = json.load(f)
    
    first_key = next(iter(meal_plan))
    if isinstance(meal_plan[first_key], dict) and "recipe" not in meal_plan[first_key]:
        meal_plan = meal_plan[first_key]

    grocery_items = {}

    from src.web_search import RecipeWebSearcher
    from src.recipe_extraction import RecipeDetector

    web_searcher = RecipeWebSearcher()
    recipe_detector = RecipeDetector()

    # --- Map recipe units to shopping-friendly units ---
    unit_mapping = {
        "cup": "can",      # chickpeas, beans, etc.
        "tbsp": "bottle",  # sauces/oils
        "tsp": "bottle",
        "oz": "oz",
        "g": "g",
        "kg": "kg",
        "lb": "lb",
        "": "unit"          # fallback
    }

    for day, details in meal_plan.items():
        recipe_name = details["recipe"]

        # KB + web fallback
        recipe = next(
            (r for r in kb.get_available_recipes() if r.name.lower() == recipe_name.lower()),
            None,
        )

        if not recipe:
            print(f"Recipe '{recipe_name}' not found in KB, attempting web search...")
            search_results = web_searcher.find_recipe_candidates(recipe_name)

            if search_results.success and search_results.search_results:
                top_url = search_results.search_results[0].url
                extraction_result = recipe_detector.extract_recipe(top_url)
                recipe = extraction_result.recipe if extraction_result.success else None

            if not recipe or not hasattr(recipe, "ingredients"):
                print(f"Could not extract recipe for '{recipe_name}', skipping")
                continue

        # Aggregate ingredients using shopping-friendly units
        for ingredient in recipe.ingredients:
            name = ingredient.name
            amount = ingredient.amount or "1"
            unit = ingredient.unit or ""
            shop_unit = unit_mapping.get(unit, unit)
            key = f"{name} ({shop_unit})" if shop_unit else name
            grocery_items.setdefault(key, []).append(amount)

    # Flatten amounts
    grocery_list = {k: ", ".join(filter(None, v)) for k, v in grocery_items.items()}

    with open(GROCERY_LIST_FILE, "w") as f:
        json.dump(grocery_list, f, indent=2)

    print(f"Grocery list saved to {GROCERY_LIST_FILE}")
    return grocery_list

def schedule_meal_plan(meal_plan_file: Path, kb: FullStackKBAnswerer):
    """Create calendar events for meals and grocery ordering."""
    creds = get_credentials()
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday as start
    # Adjust to Sunday-Saturday week
    start_of_week = start_of_week - timedelta(days=1)

    with open(meal_plan_file, "r") as f:
        meal_plan = json.load(f)
    
    first_key = next(iter(meal_plan))
    if isinstance(meal_plan[first_key], dict) and "recipe" not in meal_plan[first_key]:
        meal_plan = meal_plan[first_key]

    for i, (day, details) in enumerate(meal_plan.items()):
        recipe_name = details["recipe"]

        # Schedule meal at 6:00 PM by default
        meal_time = start_of_week + timedelta(days=i, hours=18)
        create_event_from_details(
            credentials=creds,
            title=f"{recipe_name} (Meal)",
            start_dt=meal_time,
            duration_minutes=60,
            timezone=TIMEZONE,
            calendar_id=CALENDAR_ID,
            description=details.get("reason", ""),
        )

        print(f"Scheduled {recipe_name} for {meal_time.strftime('%A %b %d %H:%M')}")

    # Schedule grocery order on Saturday (day before cooking starts on Sunday)
    grocery_order_time = start_of_week + timedelta(days=6, hours=10)
    create_event_from_details(
        credentials=creds,
        title="Grocery Order",
        start_dt=grocery_order_time,
        duration_minutes=30,
        timezone=TIMEZONE,
        calendar_id=CALENDAR_ID,
        description="Order all groceries for the upcoming week's meals",
    )
    print(f"Scheduled grocery order for {grocery_order_time.strftime('%A %b %d %H:%M')}")

def schedule_logistics(grocery_list):
    try:
        response = requests.post(
            "http://127.0.0.1:5001/schedule",
            json={"items": grocery_list},
            timeout=10,
        )
        if response.ok:
            data = response.json()
            # Save ETA to a file
            with open("output_examples/grocery_delivery_status.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"Grocery delivery scheduled! ETA: {data['eta']}")
            return True
        else:
            print("Failed to schedule delivery")
            return False
    except Exception as e:
        print(f"Logistics API error: {e}")
        return False
    
def trigger_stripe_payment(grocery_list):
    """Complete payment using fixed standard grocery prices."""
    prices = {}
    total_amount = 0

    for key in grocery_list:
        name = key.split("(")[0].strip().lower()
        if name not in STANDARD_GROCERY_UNITS:
            continue
        unit_label, unit_price = STANDARD_GROCERY_UNITS[name]  # <-- extract price from tuple
        qty = 1  # always buy 1 packaged unit
        prices[f"{name} ({unit_label})"] = (qty, unit_price)
        total_amount += unit_price

    # Stripe amount in cents
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total_amount * 100),
        currency="usd",
        payment_method_types=["card"],
        description=f"Grocery payment for {len(prices)} items"
    )

    # Confirm automatically in test mode
    stripe.PaymentIntent.confirm(
        payment_intent.id,
        payment_method="pm_card_visa"
    )

    payment_record = {
        "status": "Payment Successful",
        "amount": total_amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": prices
    }

    print(f"Payment completed: ${total_amount:.2f}, status: {payment_record['status']}")

    return payment_record


GROCERY_FILE = "output_examples/grocery_list.json"
PDF_FILE = "output_examples/grocery_receipt.pdf"

def generate_pdf_logistics_payment(logistics_file, payment_record):
    """Generate PDF combining delivery + payment info with shopping-friendly units."""
    # Load grocery delivery data
    with open(logistics_file, "r") as f:
        delivery_data = json.load(f)

    # Mock delivery details
    eta = delivery_data.get("eta", (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"))
    driver = "John Doe"
    location = "123 Main St, Tempe, AZ"
    tracking_id = f"TCK_{random.randint(100000, 999999)}"
    
    # Payment info
    payment_status = "Payment Successful"  # override for demo

    # Load grocery list
    with open(GROCERY_LIST_FILE, "r") as f:
        grocery_list = json.load(f)

    # Map recipe units to shopping-friendly units
    unit_mapping = {
        "cup": "can",
        "tbsp": "bottle",
        "tsp": "bottle",
        "oz": "oz",
        "g": "g",
        "kg": "kg",
        "lb": "lb",
        "": "unit"
    }
# Use standard grocery units regardless of recipe quantity
    prices = {}
    running_total = 0

    for key in grocery_list:
        name = key.split("(")[0].strip().lower()

        if name not in STANDARD_GROCERY_UNITS:
            continue  # skip unknown items or default to "1 unit"

        unit_label, unit_price = STANDARD_GROCERY_UNITS[name]

        qty = 1  # ALWAYS buy 1 packaged grocery unit

        prices[f"{name} ({unit_label})"] = (qty, unit_price)
        running_total += unit_price

        if running_total >= 200:
            break


    # Generate PDF
    c = canvas.Canvas(PDF_FILE, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(140, 750, "Weekly Grocery Receipt")

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 700, f"Delivery ETA: {eta}")
    c.drawString(50, 680, f"Delivery Driver: {driver}")
    c.drawString(50, 660, f"Delivery Location: {location}")
    c.drawString(50, 640, f"Tracking ID: {tracking_id}")
    c.drawString(50, 620, f"Payment Status: {payment_status}")

    # Table header
    c.drawString(50, 590, "Item")
    c.drawString(300, 590, "Qty")
    c.drawString(350, 590, "Unit Price ($)")
    c.drawString(450, 590, "Total ($)")

    y = 570
    for item, (qty, price) in prices.items():
        item_total = round(qty * price, 2)
        c.drawString(50, y, item)
        c.drawString(300, y, str(qty))
        c.drawString(350, y, f"{price:.2f}")
        c.drawString(450, y, f"{item_total:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.drawString(50, y-20, f"Total Paid: ${running_total:.2f}")
    c.drawString(50, y-40, "Thank you for using our weekly grocery service!")

    c.save()
    print(f"Receipt PDF generated: {PDF_FILE}")

def main():
    """Run the full workflow."""
    kb = FullStackKBAnswerer()
    
    # 1. Generate grocery list
    grocery_list = generate_grocery_list(MEAL_PLAN_FILE, kb)

    # 2. Schedule meal plan and grocery order
    schedule_meal_plan(MEAL_PLAN_FILE, kb)

    # 3. Schedule logistics
    schedule_logistics(grocery_list)
    # 4. Trigger payment
    payment_record = trigger_stripe_payment(grocery_list)
    # 5. Generate PDF summary
    generate_pdf_logistics_payment("output_examples/grocery_delivery_status.json", payment_record)
    print("Weekly meal workflow completed successfully!")


if __name__ == "__main__":
    main()
