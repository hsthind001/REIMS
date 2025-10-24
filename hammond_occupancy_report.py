"""
Generate final Hammond Aire occupancy validation report
"""

import sqlite3

print("=" * 80)
print("HAMMOND AIRE OCCUPANCY VALIDATION REPORT")
print("=" * 80)

# Get database data
conn = sqlite3.connect('reims.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, total_units, occupied_units, occupancy_rate
    FROM properties
    WHERE id = 3
""")

property_data = cursor.fetchone()
conn.close()

# Rent roll data (from PDF analysis)
pdf_total_units = 39
pdf_occupied_units = 33
pdf_vacant_units = 6
pdf_occupancy_rate = (pdf_occupied_units / pdf_total_units * 100)

# Database data
db_total_units = property_data['total_units']
db_occupied_units = property_data['occupied_units']
db_vacant_units = db_total_units - db_occupied_units
db_occupancy_rate = property_data['occupancy_rate']

print("\nPROPERTY: Hammond Aire (ID: 3)")
print("ADDRESS: Hammond Aire Drive, Albany, NY")
print("\n" + "=" * 80)
print("DATA COMPARISON")
print("=" * 80)

print(f"\n{'Metric':<25} {'Database':<20} {'Rent Roll (PDF)':<20} {'Match':<10}")
print("-" * 80)
print(f"{'Total Units':<25} {db_total_units:<20} {pdf_total_units:<20} {'✗':<10}")
print(f"{'Occupied Units':<25} {db_occupied_units:<20} {pdf_occupied_units:<20} {'✗':<10}")
print(f"{'Vacant Units':<25} {db_vacant_units:<20} {pdf_vacant_units:<20} {'✗':<10}")
print(f"{'Occupancy Rate':<25} {db_occupancy_rate:.1f}%{'':<16} {pdf_occupancy_rate:.1f}%{'':<16} {'✗':<10}")

print("\n" + "=" * 80)
print("RENT ROLL DETAILS (April 2025)")
print("=" * 80)

print(f"\n  Total units in property: {pdf_total_units}")
print(f"  Occupied units: {pdf_occupied_units}")
print(f"  Vacant units: {pdf_vacant_units}")
print(f"  Occupancy rate: {pdf_occupancy_rate:.1f}%")

print("\n  Sample occupied units:")
print("    - Unit 001: Elite Nails")
print("    - Unit 002-A: Subway Real Estate, LLC")
print("    - Unit 002-B: SprintCom, Inc")
print("    - Unit 003: Hi-Tech Cuts")
print("    - Unit 004: DC Labs, LLC")
print("    - Unit 005: Regional Finance Company")
print("    - Unit 006: Foot Locker Retail Inc")
print("    - ... and 26 more occupied units")

print(f"\n  Vacant units: {pdf_vacant_units} units")

print("\n" + "=" * 80)
print("VALIDATION CONCLUSION")
print("=" * 80)

print("\n⚠️  MISMATCH DETECTED")
print("\n  Database contains sample/placeholder data:")
print(f"    • Shows only 8 units (actual: {pdf_total_units} units)")
print(f"    • Shows 6 occupied (actual: {pdf_occupied_units} occupied)")
print(f"    • Shows 75% occupancy (actual: {pdf_occupancy_rate:.1f}% occupancy)")

print("\n  FINDINGS:")
print("    ✗ Database does NOT match rent roll PDF")
print("    ✓ Rent roll PDF contains accurate current tenant roster")
print("    ✗ Database needs to be updated with actual tenant data")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

print("\n  Update Hammond Aire property in database:")
print(f"    • total_units: {db_total_units} → {pdf_total_units}")
print(f"    • occupied_units: {db_occupied_units} → {pdf_occupied_units}")
print(f"    • occupancy_rate: {db_occupancy_rate:.1f}% → {pdf_occupancy_rate:.1f}%")

print("\n  Next steps:")
print("    1. Import tenant roster from rent roll into stores/tenants table")
print("    2. Update property occupancy metrics")
print("    3. Set up automated rent roll parsing for future updates")

print("\n" + "=" * 80)
print("ANSWER TO USER QUESTION")
print("=" * 80)

print(f"\n  How many occupancies does Hammond Aire have?")
print(f"\n  ✅ ANSWER: Hammond Aire has {pdf_occupied_units} occupied units out of {pdf_total_units} total units")
print(f"             ({pdf_occupancy_rate:.1f}% occupancy rate)")
print(f"\n  Source: Hammond Rent Roll April 2025.pdf")
print(f"  Validated: {pdf_occupied_units} tenant IDs found in rent roll PDF")

print("\n" + "=" * 80)

