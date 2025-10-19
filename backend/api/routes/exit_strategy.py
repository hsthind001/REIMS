from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.database import get_db
from datetime import datetime
import math

router = APIRouter()

def calculate_monthly_payment(principal, annual_rate, years=30):
    """Calculate monthly mortgage payment"""
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    return monthly_payment

def calculate_confidence_score(property_data, strategy_type, metrics):
    """Calculate confidence score based on property characteristics"""
    base_score = 70
    
    # Property-specific adjustments
    if hasattr(property_data, 'occupancy_rate') and property_data.occupancy_rate > 0.9:
        base_score += 10
    
    if hasattr(property_data, 'noi') and property_data.noi > 0:
        base_score += 5
    
    # Strategy-specific adjustments
    if strategy_type == 'hold':
        if metrics.get('irr', 0) > 10:
            base_score += 10
        if metrics.get('hold_period', 0) > 5:
            base_score += 5
    elif strategy_type == 'refinance':
        if metrics.get('new_dscr', 0) > 1.25:
            base_score += 15
        if metrics.get('monthly_savings', 0) > 0:
            base_score += 10
    elif strategy_type == 'sale':
        if metrics.get('annualized_return', 0) > 15:
            base_score += 15
        if metrics.get('net_proceeds', 0) > property_data.purchase_price:
            base_score += 10
    
    return min(95, max(50, base_score))

def generate_property_specific_pros_cons(property_data, strategy_type, metrics):
    """Generate property-specific pros and cons"""
    pros = []
    cons = []
    
    if strategy_type == 'hold':
        # Property-specific pros
        if hasattr(property_data, 'occupancy_rate') and property_data.occupancy_rate > 0.9:
            pros.append(f'High occupancy rate ({property_data.occupancy_rate * 100:.1f}%)')
        if hasattr(property_data, 'noi') and property_data.noi > 0:
            pros.append(f'Steady NOI generation (${property_data.noi:,.0f}/year)')
        pros.append('No transaction costs')
        pros.append('Tax advantages on depreciation')
        pros.append('Property appreciation potential')
        
        # Property-specific cons
        years_held = metrics.get('hold_period', 0)
        if years_held > 10:
            cons.append('Long holding period may limit liquidity')
        if hasattr(property_data, 'property_age') and property_data.property_age > 30:
            cons.append('Aging property may require capital improvements')
        cons.append('Capital tied up long-term')
        cons.append('Ongoing management costs')
        cons.append('Market downturn risk')
    
    elif strategy_type == 'refinance':
        # Property-specific pros
        if metrics.get('monthly_savings', 0) > 0:
            pros.append(f'Monthly savings of ${metrics["monthly_savings"]:,.0f}')
        if metrics.get('new_dscr', 0) > 1.25:
            pros.append(f'Strong DSCR of {metrics["new_dscr"]:.2f}x')
        if metrics.get('cash_out', 0) > 0:
            pros.append(f'Cash extraction of ${metrics["cash_out"]:,.0f}')
        pros.append('Extract equity without selling')
        pros.append('Maintain property ownership')
        pros.append('Tax-free cash extraction')
        
        # Property-specific cons
        if metrics.get('cash_out', 0) > 0:
            cons.append('Refinancing costs (typically 1-2% of loan)')
        cons.append('Extended debt obligation')
        cons.append('Rate adjustment risk')
        if metrics.get('new_dscr', 0) < 1.25:
            cons.append('Lower DSCR may limit refinancing options')
    
    elif strategy_type == 'sale':
        # Property-specific pros
        if metrics.get('annualized_return', 0) > 15:
            pros.append(f'Strong annualized return of {metrics["annualized_return"]:.1f}%')
        if metrics.get('net_proceeds', 0) > property_data.purchase_price:
            pros.append('Capital gains realized')
        pros.append('Immediate capital access')
        pros.append('Eliminate management burden')
        pros.append('Lock in appreciation gains')
        pros.append('Portfolio diversification')
        
        # Property-specific cons
        transaction_costs = metrics.get('transaction_costs', 0)
        if transaction_costs > 0:
            cons.append(f'High transaction costs (${transaction_costs:,.0f})')
        cons.append('Capital gains tax liability')
        cons.append('Loss of future income')
        cons.append('Market timing risk')
        cons.append('Difficult to replicate returns')
    
    return {'pros': pros, 'cons': cons}

def calculate_hold_strategy(property_data):
    """Calculate Hold strategy metrics"""
    # Calculate years held
    if hasattr(property_data, 'purchase_date') and property_data.purchase_date:
        years_held = (datetime.now() - property_data.purchase_date).days / 365
    else:
        # Default to 3 years if no purchase date
        years_held = 3
    
    # Calculate IRR
    if hasattr(property_data, 'purchase_price') and property_data.purchase_price and property_data.purchase_price > 0:
        if years_held > 0:
            irr = ((property_data.current_market_value / property_data.purchase_price) ** (1 / years_held) - 1) * 100
        else:
            irr = 0
    else:
        irr = 12.0  # Default IRR
    
    metrics = {
        'irr': round(irr, 2),
        'projected_noi': property_data.noi if hasattr(property_data, 'noi') else 0,
        'terminal_value': property_data.current_market_value,
        'hold_period': round(years_held, 1)
    }
    
    confidence_score = calculate_confidence_score(property_data, 'hold', metrics)
    pros_cons = generate_property_specific_pros_cons(property_data, 'hold', metrics)
    
    return {
        'irr': metrics['irr'],
        'projected_noi': metrics['projected_noi'],
        'terminal_value': metrics['terminal_value'],
        'hold_period': metrics['hold_period'],
        'confidence_score': confidence_score,
        'pros': pros_cons['pros'],
        'cons': pros_cons['cons'],
        'description': 'Continue holding the property for steady income and long-term appreciation.'
    }

def calculate_refinance_strategy(property_data, new_rate=4.25, ltv=0.75):
    """Calculate Refinance strategy metrics"""
    # New loan amount = Current value * LTV
    new_loan = property_data.current_market_value * ltv
    
    # Get current mortgage balance (default to 60% of current value if not available)
    current_mortgage_balance = getattr(property_data, 'current_mortgage_balance', property_data.current_market_value * 0.6)
    
    # Cash out = New loan - Current mortgage balance
    cash_out = new_loan - current_mortgage_balance
    
    # Calculate monthly payments
    current_rate = getattr(property_data, 'current_mortgage_rate', 5.5)
    old_payment = calculate_monthly_payment(current_mortgage_balance, current_rate)
    new_payment = calculate_monthly_payment(new_loan, new_rate)
    monthly_savings = old_payment - new_payment
    
    # DSCR = NOI / Annual Debt Service
    annual_debt_service = new_payment * 12
    noi = getattr(property_data, 'noi', property_data.current_market_value * 0.08)
    new_dscr = (noi / annual_debt_service) if annual_debt_service > 0 else 0
    
    metrics = {
        'monthly_savings': round(monthly_savings, 2),
        'new_dscr': round(new_dscr, 2),
        'cash_out': round(cash_out, 2),
        'new_rate': new_rate
    }
    
    confidence_score = calculate_confidence_score(property_data, 'refinance', metrics)
    pros_cons = generate_property_specific_pros_cons(property_data, 'refinance', metrics)
    
    return {
        'monthly_savings': metrics['monthly_savings'],
        'new_dscr': metrics['new_dscr'],
        'cash_out': metrics['cash_out'],
        'new_rate': metrics['new_rate'],
        'confidence_score': confidence_score,
        'pros': pros_cons['pros'],
        'cons': pros_cons['cons'],
        'description': 'Refinance to extract equity while maintaining ownership and improving cash flow.'
    }

def calculate_sale_strategy(property_data):
    """Calculate Sale strategy metrics"""
    sale_price = property_data.current_market_value
    
    # Transaction costs: 5.8% of sale price
    transaction_costs = sale_price * 0.058
    
    # Get current mortgage balance
    current_mortgage_balance = getattr(property_data, 'current_mortgage_balance', property_data.current_market_value * 0.6)
    
    # Net proceeds = Sale price - Transaction costs - Mortgage balance
    net_proceeds = sale_price - transaction_costs - current_mortgage_balance
    
    # Calculate annualized return
    if hasattr(property_data, 'purchase_date') and property_data.purchase_date:
        years_held = (datetime.now() - property_data.purchase_date).days / 365
    else:
        years_held = 3
    
    if hasattr(property_data, 'purchase_price') and property_data.purchase_price and property_data.purchase_price > 0:
        if years_held > 0:
            total_return = (net_proceeds / property_data.purchase_price)
            annualized_return = (total_return ** (1 / years_held) - 1) * 100
        else:
            annualized_return = 0
    else:
        annualized_return = 18.5  # Default return
    
    metrics = {
        'net_proceeds': round(net_proceeds, 2),
        'transaction_costs': round(transaction_costs, 2),
        'annualized_return': round(annualized_return, 2),
        'sale_price': sale_price
    }
    
    confidence_score = calculate_confidence_score(property_data, 'sale', metrics)
    pros_cons = generate_property_specific_pros_cons(property_data, 'sale', metrics)
    
    return {
        'net_proceeds': metrics['net_proceeds'],
        'transaction_costs': metrics['transaction_costs'],
        'annualized_return': metrics['annualized_return'],
        'sale_price': metrics['sale_price'],
        'confidence_score': confidence_score,
        'pros': pros_cons['pros'],
        'cons': pros_cons['cons'],
        'description': 'Sell the property to realize gains and redeploy capital into new opportunities.'
    }

def determine_recommended_strategy(hold_metrics, refinance_metrics, sale_metrics):
    """Determine the recommended strategy based on metrics"""
    # Simple scoring system
    scores = {
        'hold': hold_metrics['confidence_score'],
        'refinance': refinance_metrics['confidence_score'],
        'sale': sale_metrics['confidence_score']
    }
    
    # Additional factors
    if refinance_metrics['monthly_savings'] > 0 and refinance_metrics['new_dscr'] > 1.25:
        scores['refinance'] += 10
    
    if sale_metrics['annualized_return'] > 15:
        scores['sale'] += 5
    
    if hold_metrics['irr'] > 12:
        scores['hold'] += 5
    
    return max(scores, key=scores.get)

@router.get("/analyze/{property_id}")
async def analyze_exit_strategy(property_id: int, db: Session = Depends(get_db)):
    """Analyze exit strategies for a specific property"""
    try:
        # Fetch property data using raw SQL
        result = db.execute(
            text("SELECT * FROM properties WHERE id = :property_id"),
            {"property_id": property_id}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Parse metadata if available
        metadata = {}
        if result.property_metadata:
            try:
                import json
                metadata = json.loads(result.property_metadata)
            except:
                metadata = {}
        
        # Create a property data object with the available fields
        property_data = type('PropertyData', (), {
            'id': result.id,
            'name': result.property_id,  # Using property_id as name
            'address': result.address,
            'property_type': result.property_type,
            'current_market_value': result.value or 10000000,
            'noi': metadata.get('noi', (result.value or 10000000) * 0.08),
            'purchase_price': metadata.get('purchase_price', (result.value or 10000000) * 0.8),
            'purchase_date': datetime.strptime(metadata.get('purchase_date', '2020-01-01'), '%Y-%m-%d'),
            'current_mortgage_balance': (result.value or 10000000) * 0.6,  # 60% LTV
            'current_mortgage_rate': 5.5,  # Default rate
            'occupancy_rate': metadata.get('occupancy_rate', 0.92),
            'property_age': 2024 - metadata.get('year_built', 2015)
        })()
        
        # Calculate strategies
        hold_analysis = calculate_hold_strategy(property_data)
        refinance_analysis = calculate_refinance_strategy(property_data)
        sale_analysis = calculate_sale_strategy(property_data)
        
        # Determine recommended strategy
        recommended_strategy = determine_recommended_strategy(hold_analysis, refinance_analysis, sale_analysis)
        
        # Calculate years held for display
        if hasattr(property_data, 'purchase_date') and property_data.purchase_date:
            years_held = (datetime.now() - property_data.purchase_date).days / 365
        else:
            years_held = 3
        
        return {
            "success": True,
            "property_id": property_id,
            "property_name": property_data.name,
            "purchase_price": getattr(property_data, 'purchase_price', property_data.current_market_value * 0.8),
            "current_value": property_data.current_market_value,
            "noi": getattr(property_data, 'noi', property_data.current_market_value * 0.08),
            "years_held": round(years_held, 1),
            "recommended_strategy": recommended_strategy,
            "hold": hold_analysis,
            "refinance": refinance_analysis,
            "sale": sale_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
