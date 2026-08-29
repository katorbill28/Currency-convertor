"""Quick prototype for converting hardcoded INR expenses to USD."""

INR_TO_USD_RATE = 95.24
expenses_inr = [250, 799, 1250.50, 3499, 10200]

print("INR to USD Expense Conversion")
print(f"Exchange rate: 1 USD = {INR_TO_USD_RATE} INR")
print()

for amount_inr in expenses_inr:
    amount_usd = amount_inr / INR_TO_USD_RATE
    print(f"INR {amount_inr:.2f} = USD {amount_usd:.2f}")
