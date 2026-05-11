import numpy as np
import pandas as pd

# program to add new column in the existing data set
data={"Name":['Jaya','Raj','Deepa'],
      "Age":[39,39,39],
      "city":["Bangalore","Delhi","Bombay"],
      "Salary":[33000,70000,90000],
      "Performance_Score":[67,85,95]}
print(data)
df = pd.DataFrame(data)
df["Bonus"] = df['Salary'] * 0.1
print(df)

# insert new column at specific position
df.insert(0,"Employee Id",[101,102,103])
print ("After Adding new columns")
print(df)

# Updating values df.loc[row_index,"Column Name"] = value

df.loc[2,"Age"] = 40
print("After age modification")
print(df)

# increase salary by 5%

df['Salary'] = df['Salary'] * 1.05
print("After Salary increment\n",df)

# Remove columns from Data set, inplace = True --> to modify orginal data

df.drop(columns=["Age","Bonus"],inplace=True)

print("Data Set after Age column removed")
print(df)
