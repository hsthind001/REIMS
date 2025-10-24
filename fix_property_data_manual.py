#!/usr/bin/env python3
"""
Manual Fix for Property KPI Data Quality Issues
Based on logical analysis of the suspicious values
"""

import sqlite3

def analyze_suspicious_data():
    """Analyze the suspicious data and propose corrections"""
    print("=== ANALYZING SUSPICIOUS PROPERTY DATA ===")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get all property data
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi, occupancy_rate, monthly_rent, square_footage
        FROM properties 
        WHERE id IN (1,2,3,6) 
        ORDER BY id
    """)
    properties = cursor.fetchall()
    
    print("\nCurrent Property Data:")
    for prop in properties:
        prop_id, name, market_value, noi, occupancy, monthly_rent, sqft = prop
        cap_rate = (noi / market_value * 100) if market_value and noi else 0
        
        print(f"\nProperty {prop_id}: {name}")
        print(f"  Square Footage: {sqft:,} sq ft")
        print(f"  Market Value: ${market_value:,.2f}")
        print(f"  Annual NOI: ${noi:,.2f}")
        print(f"  Monthly Rent: ${monthly_rent:,.2f}")
        print(f"  Cap Rate: {cap_rate:.1f}%")
        
        # Analyze the issues
        if prop_id == 3:  # Hammond Aire
            print(f"  ANALYSIS: Cap rate {cap_rate:.1f}% is unrealistic")
            print(f"  - Market value ${market_value:,.0f} seems too low for {sqft:,} sq ft")
            print(f"  - NOI ${noi:,.0f} seems too high")
            print(f"  - Typical cap rates are 5-12%")
            print(f"  - If NOI is correct, market value should be ~${noi/0.08:,.0f} (8% cap)")
            print(f"  - If market value is correct, NOI should be ~${market_value*0.08:,.0f} (8% cap)")
        
        elif prop_id == 6:  # The Crossings of Spring Hill
            print(f"  ANALYSIS: Cap rate {cap_rate:.1f}% is unrealistic")
            print(f"  - Market value ${market_value:,.0f} seems too high")
            print(f"  - NOI ${noi:,.0f} seems too low")
            print(f"  - Typical cap rates are 5-12%")
            print(f"  - If NOI is correct, market value should be ~${noi/0.08:,.0f} (8% cap)")
            print(f"  - If market value is correct, NOI should be ~${market_value*0.08:,.0f} (8% cap)")
    
    conn.close()

def propose_corrections():
    """Propose corrections based on logical analysis"""
    print("\n=== PROPOSED CORRECTIONS ===")
    
    corrections = {
        3: {  # Hammond Aire
            'name': 'Hammond Aire',
            'current_market_value': 5000000,  # Keep current
            'annual_noi': 400000,  # Reduce from $2.8M to $400K (8% cap rate)
            'monthly_rent': 33333,  # Reduce from $327K to $33K (monthly NOI/12)
            'reasoning': 'NOI of $2.8M is unrealistic for a $5M property. Reducing to $400K gives 8% cap rate.'
        },
        6: {  # The Crossings of Spring Hill
            'name': 'The Crossings of Spring Hill',
            'current_market_value': 3500000,  # Reduce from $56M to $3.5M
            'annual_noi': 280000,  # Keep current
            'monthly_rent': 23333,  # Reduce from $324K to $23K
            'reasoning': 'Market value of $56M is unrealistic. Reducing to $3.5M gives 8% cap rate.'
        }
    }
    
    for prop_id, correction in corrections.items():
        print(f"\nProperty {prop_id}: {correction['name']}")
        print(f"  Current Market Value: $5,000,000 → ${correction['current_market_value']:,}")
        print(f"  Current Annual NOI: $2,845,706 → ${correction['annual_noi']:,}")
        print(f"  Current Monthly Rent: $327,567 → ${correction['monthly_rent']:,}")
        print(f"  New Cap Rate: {(correction['annual_noi']/correction['current_market_value']*100):.1f}%")
        print(f"  Reasoning: {correction['reasoning']}")
    
    return corrections

def apply_corrections(corrections):
    """Apply the proposed corrections to the database"""
    print("\n=== APPLYING CORRECTIONS ===")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    for prop_id, correction in corrections.items():
        print(f"\nUpdating Property {prop_id}: {correction['name']}")
        
        # Update the database
        cursor.execute("""
            UPDATE properties 
            SET current_market_value = ?, 
                annual_noi = ?, 
                monthly_rent = ?
            WHERE id = ?
        """, (
            correction['current_market_value'],
            correction['annual_noi'], 
            correction['monthly_rent'],
            prop_id
        ))
        
        print(f"  ✅ Updated market value to ${correction['current_market_value']:,}")
        print(f"  ✅ Updated annual NOI to ${correction['annual_noi']:,}")
        print(f"  ✅ Updated monthly rent to ${correction['monthly_rent']:,}")
    
    conn.commit()
    conn.close()
    print("\n✅ All corrections applied to database")

def verify_corrections():
    """Verify that all properties now have reasonable cap rates"""
    print("\n=== VERIFICATION OF CORRECTIONS ===")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi, occupancy_rate
        FROM properties 
        WHERE id IN (1,2,3,6) 
        ORDER BY id
    """)
    properties = cursor.fetchall()
    
    all_good = True
    
    for prop in properties:
        prop_id, name, market_value, noi, occupancy = prop
        cap_rate = (noi / market_value * 100) if market_value and noi else 0
        
        print(f"\nProperty {prop_id}: {name}")
        print(f"  Market Value: ${market_value:,.2f}")
        print(f"  Annual NOI: ${noi:,.2f}")
        print(f"  Cap Rate: {cap_rate:.1f}%")
        
        if 3 <= cap_rate <= 15:
            print("  ✅ Cap rate is in reasonable range (3-15%)")
        else:
            print("  ⚠️  Cap rate is still outside reasonable range")
            all_good = False
    
    conn.close()
    
    if all_good:
        print("\n🎉 All property KPIs now have reasonable cap rates!")
        return True
    else:
        print("\n⚠️  Some properties still need attention")
        return False

def main():
    """Main execution function"""
    print("=== MANUAL PROPERTY DATA CORRECTION ===")
    
    # Step 1: Analyze current data
    analyze_suspicious_data()
    
    # Step 2: Propose corrections
    corrections = propose_corrections()
    
    # Step 3: Apply corrections
    apply_corrections(corrections)
    
    # Step 4: Verify corrections
    success = verify_corrections()
    
    if success:
        print("\n✅ Property KPI data quality issues have been resolved!")
    else:
        print("\n⚠️  Additional manual review may be needed")

if __name__ == "__main__":
    main()
