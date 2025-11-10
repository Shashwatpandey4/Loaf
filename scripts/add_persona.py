#!/usr/bin/env python3
"""Script to add a persona to the database via terminal prompts."""

import uuid
from loguru import logger

from src.models.contracts import Persona
from scripts.utils import insert_persona_to_db


def get_user_input():
    """Get persona information from user via terminal prompts."""
    print("\n=== Add New Persona ===\n")
    
    # Get name
    name = input("Enter your name: ").strip()
    while not name:
        print("Name cannot be empty!")
        name = input("Enter your name: ").strip()
    
    # Get dietary restriction
    print("\nDietary Restrictions:")
    print("1. Vegetarian")
    print("2. Non-Vegetarian")
    dietary_choice = input("Select option (1 or 2): ").strip()
    
    while dietary_choice not in ["1", "2"]:
        print("Invalid choice! Please select 1 or 2.")
        dietary_choice = input("Select option (1 or 2): ").strip()
    
    dietary_restrictions = "Vegetarian" if dietary_choice == "1" else "Non-Vegetarian"
    
    # Get medical condition
    print("\nMedical Conditions:")
    print("1. High Blood Pressure")
    print("2. Diabetes")
    print("3. None")
    medical_choice = input("Select option (1, 2, or 3): ").strip()
    
    while medical_choice not in ["1", "2", "3"]:
        print("Invalid choice! Please select 1, 2, or 3.")
        medical_choice = input("Select option (1, 2, or 3): ").strip()
    
    if medical_choice == "1":
        medical_condition = "High Blood Pressure"
    elif medical_choice == "2":
        medical_condition = "Diabetes"
    else:
        medical_condition = "None"
    
    return name, dietary_restrictions, medical_condition


def main():
    """Main function to add persona to database."""
    try:
        # Get user input
        name, dietary_restrictions, medical_condition = get_user_input()
        
        # Create Persona object
        persona = Persona(
            id=str(uuid.uuid4()),
            name=name,
            medical_condition=medical_condition,
            dietary_restrictions=dietary_restrictions
        )
        
        # Insert into database
        insert_persona_to_db(persona)
        
        print("\n✓ Persona added successfully!")
        print(f"\nDetails:")
        print(f"  Name: {persona.name}")
        print(f"  Dietary Restrictions: {persona.dietary_restrictions}")
        print(f"  Medical Condition: {persona.medical_condition}")
        print(f"  ID: {persona.id}")
        
        logger.info(f"Added persona: {persona.name} (ID: {persona.id})")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error adding persona: {e}")
        logger.error(f"Error adding persona: {e}")


if __name__ == "__main__":
    main()

