#%%

def calculate_tax(income: float, deductions: float = 0, contribution_401k=0) -> dict:
    """
    Calculate income tax based on tax brackets, considering deductions.
    
    Args:
        income (float): Gross income
        deductions (float): Tax deductions (default: 0)
        contribution_401k (float): Contribution to 401k (default: 0)
    Returns:
        dict: Dictionary containing tax calculation details
    """
    # Tax brackets and rates
    brackets = [
        {"min": 0, "max": 11000, "rate": 0.10},
        {"min": 11001, "max": 44725, "rate": 0.12},
        {"min": 44726, "max": 95375, "rate": 0.22},
        {"min": 95376, "max": 182100, "rate": 0.24},
        {"min": 182101, "max": 231250, "rate": 0.32},
        {"min": 231251, "max": 578125, "rate": 0.35},
        {"min": 578126, "max": float('inf'), "rate": 0.37}
    ]
    
    # Calculate taxable income
    taxable_income = max(income - deductions- contribution_401k, 0)
    total_tax = 0
    remaining_income = taxable_income
    
    # Calculate tax for each bracket
    for i, bracket in enumerate(brackets):
        prev_bracket_max = brackets[i-1]["max"] if i > 0 else 0
        
        # Calculate income in current bracket
        income_in_bracket = min(
            max(remaining_income, 0),
            bracket["max"] - prev_bracket_max
        )
        
        # Calculate tax for current bracket
        tax_in_bracket = income_in_bracket * bracket["rate"]
        total_tax += tax_in_bracket
        
        # Update remaining income
        remaining_income -= income_in_bracket
        
        # Break if no more income to tax
        if remaining_income <= 0:
            break
    
    # Round monetary values to 2 decimal places
    total_tax = round(total_tax, 2)
    after_tax_income = round(income - total_tax, 2)
    by_weekly_payment = round((after_tax_income - contribution_401k)/26, 1)
    effective_tax_rate = f"{(total_tax / income * 100):.2f}%" if income > 0 else "0.00%"
    
    # Return results
    return {
        "gross_income": income,
        "deductions": deductions,
        "contribution 401k": contribution_401k,
        "taxable_income": taxable_income,
        "total_tax": total_tax,
        "after_tax_income": after_tax_income,
        "effective_tax_rate": effective_tax_rate,
        "by_weekly_payment": by_weekly_payment
    }


# Example usage
if __name__ == "__main__":
    # Example 1: $100,000 income with $12,000 deductions
    example1 = calculate_tax(145000, 14500, 20000)
    for key, value in example1.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: $250,000 income with $25,000 deductions
    example2 = calculate_tax(140000, 30000, 20000)
    for key, value in example2.items():
        print(f"{key}: {value}")

# %%
total_income = 0
total_tax = 0
s = 140000
for i in range(30): 
    total_income += calculate_tax(s, 14500)['after_tax_income'] 
    total_tax += calculate_tax(s, 14500)['total_tax']
    s = s*1.05    

print(total_income)
print(total_tax)
# %%
