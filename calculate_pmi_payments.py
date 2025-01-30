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
                                insurance_rate=0.3, home_appreciation=5.0,
                                rent=2300, annual_rent_increase=0.03, 
                                market_return=0.08):
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
        rent (float): Monthly rent amount
        annual_rent_increase (float): Annual rent increase rate as percentage (default 3.0%)
        market_return (float): Expected annual return rate on investments (default 8.0%)
    
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
    df['total_rent'] = rent_payment(rent, years, annual_rent_increase)[1]
    df['paid_rent'] = rent_payment(rent, years, annual_rent_increase)[0]
    df['monthly_rent'] = rent_payment(rent, years, annual_rent_increase)[2]

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

    df['savings_w_investment'] = yearly_savings(df, down_payment=down_payment, col = 'Annual payment difference', market_return=market_return)
    df['home_equity'] = df['home_value'] - df['remaining_balance']
    df['difference_w_investment'] = df['savings_w_investment'] - df['home_equity']
    return df
"""
    print(f"\nMortgage parameters:")
    print(f"Home Price: ${home_price:,.0f}")
    print(f"Down Payment: ${down_payment:,.0f} ({(down_payment/home_price)*100:.0f}%)")
    print(f"Loan Amount: ${loan_amount:,.0f}")
    print(f"Interest Rate: {annual_rate}%")
    print(f"Maintenance Rate: {maintenance_rate}%")
    print(f"Property Tax Rate: {property_tax_rate}%")
    print(f"Insurance Rate: {insurance_rate}%")
    print(f"Term: {years} years")
    print(f'\nMortgage costs and value analysis:')
    print(f"Inital monrthly payment: ${df['monthly_payment'].iloc[0]:,.0f}")
    print(f"Final Monthly Payment: ${df['monthly_payment'].iloc[-1]:,.0f}")
    print(f"Total cost of owning(Mortgage payment + PMI")
    print(f"+ insurance + property tax + Maintenance):")
    print(f" ${df['total_amount_paid'].iloc[-1]:,.0f}")
    print(f"Initial Home Value: ${home_price:,.0f}")
    print(f"Final Home Value: ${final_home_value:,.0f}")
    print(f"Total Appreciation: ${total_appreciation:,.0f} ({(total_appreciation/home_price)*100:.1f}%)")

    print(f'\nRent costs and value analysis:')
    print(f"Initial Monthly Rent: ${df['monthly_rent'].iloc[0]:,.0f}")
    print(f"Final Monthly Rent: ${df['monthly_rent'].iloc[-1]:,.0f}")
    print(f"Total Rent Paid: ${df['total_rent'].iloc[-1]:,.0f}")
    
    print(f'If the yearly difference between cost of owing vs rent is invested \n by the end of 30 years you will have: ${df["savings_w_investment"].iloc[-1]:,.0f}')
    print(f'net difference: ${df["savings_w_investment"].iloc[-1] - df["home_value"].iloc[-1]:,.0f}')
"""
    

#%%
# Calculate for a $400,000 home with 3% down
home_price = 600000
df_3dp = calculate_complete_mortgage_analysis(home_price, home_price*0.03, 30, 6, rent=2500)
df_10dp = calculate_complete_mortgage_analysis(home_price, home_price*0.10, 30, 6, rent=2500)
df_20dp = calculate_complete_mortgage_analysis(home_price, home_price*0.20, 30, 6, rent=2500)

# %%
print(f"3% of home value: ${home_price*0.03:,.0f}")
print(f"10% of home value: ${home_price*0.10:,.0f}")
print(f"20% of home value: ${home_price*0.20:,.0f}")
print('difference between 3% and 10% down payment after 10 years:',)
print(f"${df_3dp['total_amount_paid'].iloc[10] - df_10dp['total_amount_paid'].iloc[10]:,.0f}")
print('value of difference (7% of home value) if invested:',)
print(f"${compound_interest(home_price*(0.10 - 0.03), 0.08, 10):,.0f}")

print('difference between 3% and 20% down payment after 10 years:',)
print(f"${df_3dp['total_amount_paid'].iloc[10] - df_20dp['total_amount_paid'].iloc[10]:,.0f}")
print('value of of difference (17% of home value) if invested:',)
print(f"${compound_interest(home_price*(0.20 - 0.03), 0.08, 10):,.0f}")
# %%
import numpy as np
import matplotlib.pyplot as plt
investment_saving = []
home_prices = np.linspace(350000, 750000, 9)
home_values = []
saving_w_investments = []
for home_price in home_prices:
    df = calculate_complete_mortgage_analysis(home_price, home_price*0.03, 30, 6, rent=2500)
    home_value = df['home_value'].iloc[10]
    home_values.append(home_value)
    
    saving_w_investment = df['savings_w_investment'].iloc[10]
    saving_w_investments.append(saving_w_investment)

    investment_saving.append(home_value - saving_w_investment)

plt.figure(figsize=(10, 6))
plt.plot(home_prices, investment_saving, marker='o')
plt.title('Investment Saving vs Home Price')
plt.xlabel('Home Price')
plt.ylabel('Investment Saving')
plt.grid()
# %%
