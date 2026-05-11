import numpy as np
import pandas as pd
data = pd.read_csv('Employee_details.csv')

print(data)

data1 = pd.read_json("sample_Data.json")
print(data1)
"""print("Basic Data Set of first 5 rows to understand the data set")
print(data.head())

# Checking the missing values
print("Missing Values in data set")
print(data.isnull().sum())

#replace missing value with some values
data['Salary'].fillna({data['Salary']:data['Salary'].mean()}, inplace = True)"""