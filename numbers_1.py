import pandas as pd
import random

# Generate 1,000,000 phone numbers
phone_numbers = ['237656' + str(i).zfill(6) for i in range(701)]

# Shuffle the phone numbers
random.shuffle(phone_numbers)

# Create a DataFrame
df = pd.DataFrame(phone_numbers, columns=['Numbers'])

# Write to an Excel file
df.to_excel('phone_numbersamata.xlsx', index=False)

