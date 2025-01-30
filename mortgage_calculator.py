# %%
import pandas as pd


def rent_payment(rent, years, annual_increase):
    total_rent = 0 
    rents = []
    total_rents = []
    monthly_rent = []
    for n in range(years): 
        total_rent += rent
        rents.append(round(rent, 1))
        total_rents.append(round(total_rent, 1))
        monthly_rent.append(round(rent/12, 1))
        rent = (1+annual_increase)*rent
    return rents, total_rents, monthly_rent

def yearly_savings(df, down_payment, col = 'Annual payment difference', market_return = 0.08):
    initial_savings = df[col].iloc[0] + down_payment *(1+market_return)
    savings = [initial_savings]
    for i in df[col].iloc[:-1]:
        saving = initial_savings*(1+market_return) + i
        initial_savings = saving
        savings.append(round(saving, 2))
    return savings

def compound_interest(principal, rate, years):
    total = principal*(1+rate)**years
    return total

def calculate_complete_mortgage_analysis(home_price, down_payment, years, annual_rate, 
                                maintenance_rate=1, property_tax_rate=0.9, 
                                insurance_rate=0.3, home_appreciation=5.0):
    """
    Calculate complete mortgage analysis including amortization, PMI payments, maintenance costs,
    property taxes, and home insurance.
    
    Args:
        home_price (float): Total price of the home
        down_payment (float): Down payment amount
        years (int): Term of mortgage in years
        annual_rate (float): Annual interest rate as percentage (e.g., 5.5 for 5.5%)
        maintenance_rate (float): Annual maintenance cost as percentage of home value (default 1.0%)
        property_tax_rate (float): Annual property tax rate as percentage of home value (default 1.15%)
        insurance_rate (float): Annual home insurance rate as percentage of home value (default 0.5%)
        home_appreciation (float): Annual home appreciation rate as percentage of home value (default 5.0%)    

    Returns:
        pandas.DataFrame: DataFrame containing yearly mortgage and rent details and all associated costs and return on investment
    """
    # Calculate initial loan amount
    loan_amount = home_price - down_payment
    
    # Calculate monthly rate and number of payments
    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    
    # Calculate monthly payment
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    # Initialize tracking variables
    remaining_balance = loan_amount
    yearly_data = []
    current_home_value = home_price
    
    # Calculate initial LTV ratio
    initial_ltv = (loan_amount / home_price) * 100
    
    total_amount_paid = 0
    for year in range(1, years + 1):
        yearly_principal = 0
        yearly_interest = 0
        
        # Calculate monthly payments for the year
        for _ in range(12):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            yearly_principal += principal_payment
            yearly_interest += interest_payment
            remaining_balance -= principal_payment
        
        # Calculate PMI for this year
        current_ltv = (remaining_balance / home_price) * 100
        monthly_pmi = (remaining_balance * 0.005) / 12 if current_ltv > 80 else 0
        
        # Calculate monthly costs based on current home value
        monthly_maintenance = (current_home_value * (maintenance_rate / 100)) / 12
        monthly_property_tax = (current_home_value * (property_tax_rate / 100)) / 12
        monthly_insurance = (current_home_value * (insurance_rate / 100)) / 12
        total_amount_paid += (monthly_payment + monthly_pmi + monthly_maintenance + monthly_property_tax + monthly_insurance)*12
        # Create yearly summary
        yearly_summary = {
            'year': year,
            'home_value': round(current_home_value, 2),
            'monthly_payment': round(monthly_payment, 2),
            'principal_paid': round(yearly_principal, 2),
            'interest_paid': round(yearly_interest, 2),
            'remaining_balance': round(max(0, remaining_balance), 2),
            'monthly_pmi': round(monthly_pmi, 2),
            'monthly_maintenance': round(monthly_maintenance, 2),
            'monthly_property_tax': round(monthly_property_tax, 2),
            'monthly_insurance': round(monthly_insurance, 2),
            'total_monthly_payment': round(monthly_payment + monthly_pmi + 
                                        monthly_maintenance + monthly_property_tax + 
                                        monthly_insurance, 2),
            'total_amount_paid': round(total_amount_paid, 2)
        }
        
        yearly_data.append(yearly_summary)
        # Update home value for next year
        current_home_value *= 1 + (home_appreciation / 100)
    
    # Create DataFrame
    df = pd.DataFrame(yearly_data)
    rent = rent*12

    # Calculate summary statistics
    total_interest = df['interest_paid'].sum()
    total_pmi = df['monthly_pmi'].sum() * 12
    total_maintenance = df['monthly_maintenance'].sum() * 12
    total_property_tax = df['monthly_property_tax'].sum() * 12
    total_insurance = df['monthly_insurance'].sum() * 12
    final_home_value = df['home_value'].iloc[-1]

    total_appreciation = final_home_value - home_price

    df['Annual payment difference'] = (df['total_monthly_payment'] - df['monthly_rent'])*12
    df['net payment difference'] = df['Annual payment difference'].cumsum()

    df['savings_w_investment'] = yearly_savings(df, down_payment=down_payment, col = 'Annual payment difference')
    df['home_equity'] = df['home_value'] - df['remaining_balance']
    df['difference_w_investment'] = df['savings_w_investment'] - df['home_equity']
    return df

# %%
