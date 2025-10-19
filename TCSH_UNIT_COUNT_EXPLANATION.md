# TCSH Unit Count Explanation

## Question: Why 37 Units Instead of 38?

### Summary
The rent roll document contains **38 entries**, but only **37 are actual leases**. One entry is an expense allocation, not a lease.

---

## The 38 Entries in the Rent Roll

Looking at the TCSH Rent Roll April 2025, there are 38 total entries:

1. **Target #-2362** - [NAP]-Exp Only
2. Units 1000-1019 (20 units)
3. Unit 1021
4. Units 1022-1030 (9 units)  
5. Units 1036A, 1036B/1036C (3 units)
6. Units 1037-1041 (5 units)
7. Units 2000, 2008, 2020 (3 units)

**Total: 38 entries**

---

## Why Only 37 Leases?

### The Target #-2362 Entry

```
Target #-2362
[NAP] (t0000351)
[NAP]-Exp Only
0.00 sqft
Monthly Rent: $0.00
Annual Rent: $0.00
```

**[NAP]** = **Non-Anchor Pad**  
**Exp Only** = **Expense Only**

This entry is:
- **NOT a lease** - it's an expense allocation
- Has **0 square feet** of rentable space
- Has **$0 rent** (no revenue)
- Used for tracking shared expenses or common area costs
- Not counted in the lease total

---

## Evidence from Rent Roll

### Page 6 - Summary of Lease Types
```
# of Leases    Total Area
Retail NNN     37        219,905.00
VACANT         0         0.00
```

The rent roll explicitly states **37 leases**, not 38.

### Occupancy Summary
```
Occupied Area:  219,905.00 sqft (100%)
Vacant Area:    0.00 sqft (0%)
Total:          219,905.00 sqft
```

The total area is **219,905 sqft**, which does NOT include the Target entry (0 sqft).

---

## Decision

**Import 37 units, exclude Target #-2362**

Reasons:
1. Rent roll officially counts 37 leases
2. Target entry has no area or rent
3. It's an expense allocation, not a tenant lease
4. Total sqft calculation excludes it (219,905)
5. Standard real estate practice: NAP-Exp Only entries are not leases

---

## Impact on Occupancy

**Correct Calculation:**
- 37 leased units
- 37 occupied units
- 0 vacant units
- **100% occupancy rate** ✅

---

## Conclusion

The rent roll contains 38 entries, but **Target #-2362 is not a lease** - it's an administrative expense allocation entry. Therefore, we correctly import **37 actual leases** to achieve the **100% occupancy** stated in the rent roll.

