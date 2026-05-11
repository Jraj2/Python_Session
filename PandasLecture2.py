import numpy as np
import pandas as pd

# program to save dictionary data into .csv file
data={"Name":['Jaya','Raj','Deepa'],
      "Age":[39,39,39],
      "city":["Bangalore","Delhi","Bombay"],
      "Salary":[33000,70000,90000],
      "Performance_Score":[67,85,95]}
print(data)
df=pd.DataFrame(data)
print(df)
print(f'Shape:{df.shape}')
print(f'Columns:{df.columns}')

#print single column value
name = df['Name']
print(name)

#Selecting multiple object
subset =df[['Name','Salary']]
print(subset)

#Apply filter
filtered = df[(df['Age']>24) & (df['Salary']>50000)]

print(filtered)

filtered_or = df[(df['Performance_Score']>80) | (df['Salary']>50000)]

print(filtered_or)