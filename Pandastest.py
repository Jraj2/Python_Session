# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


plt.show()

# Group income by source (using Category column)
income_sources = income_data.groupby('Category')['Amount'].sum().reset_index()
income_sources.rename(columns={'Category': 'Source', 'Amount': 'Total_Amount'}, inplace=True)

# Load the personal finance dataset
data = pd.read_csv('personal_finance_dataset.csv')

income_data = data [float == 'Income'].copy()
expense_data = data [float == 'Expense'].copy()
# Display first few rows to understand structure
#data.head()
print(data.head())
print("Shape of the dataset:", data.shape)
print("Data types:\n", data.dtypes)
print("Null values in each column:\n", data.isnull().sum())
print("last 5 rows of the dataset:",data.tail())

#display statistical summary
print("Statistical summary of the dataset:")
print(data.describe())

#Display categorical data info
print("Categorical data info:")
print(data.select_dtypes(include=['object']).nunique())

# Check the null values in each column
print("Null values in each column:\n", data.isnull().sum())

# Convert data to date time column
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Handing missing values by filling with mean for numerical columns
numerical_cols = data.select_dtypes(include=[np.number]).columns

#ensure amount is numeric
data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')

#Create absolute amount column
data['Absolute_Amount'] = data['Amount'].abs()

# Extract month, day_of_week, year from date
data['Month'] = data['Date'].dt.month   
data['Day_of_Week'] = data['Date'].dt.dayofweek
data['Year'] = data['Date'].dt.year

# Seperate income and expense
income_data = data[data['Amount'] > 0]  
expense_data = data[data['Amount'] < 0]

# Calculate total income and expense
total_income = income_data['Amount'].sum()
total_expense = expense_data['Amount'].sum()

#Calculate net savings
net_savings = total_income + total_expense

# Find Largest transactions
largest_income = income_data['Amount'].max()

# Group expense by category
expense_by_category = expense_data.groupby('Category')['Absolute_Amount'].sum().sort_values(ascending=False)

# Data Visualization using matplotlib and seaborn
# Monthly Income and Expense Trend  
monthly_data = data.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
plt.figure(figsize=(12, 6))     
sns.lineplot(data=monthly_data, x='Month', y='Amount', hue='Year', marker='o')
plt.title('Monthly Income and Expense Trend')
plt.xlabel('Month')
plt.ylabel('Amount')
plt.legend(title='Year')
plt.show()

# Expense Distribution by Category
plt.figure(figsize=(10, 6)) 
expense_by_category.plot(kind='bar')
plt.title('Expense Distribution by Category')
plt.xlabel('Category')
plt.ylabel('Total Expense')
plt.show()

# Daily Expense Heatmap
daily_expense = expense_data.pivot_table(index='Day_of_Week', columns='month', values='Absolute_Amount', aggfunc='sum').fillna(0)
plt.figure(figsize=(10, 6))     
sns.heatmap(daily_expense, annot=True, fmt=".0f", cmap='YlGnBu')
plt.title('Daily Expense Heatmap')
plt.xlabel('Month')
plt.ylabel('Day of Week')
plt.show()

# Use of Pie Chat to show income and expense ratio quarterly
quarterly_data = data.copy()    
quarterly_data['Quarter'] = quarterly_data['Date'].dt.to_period('Q')
quarterly_summary = quarterly_data.groupby('Quarter')['Amount'].sum().reset_index()
plt.figure(figsize=(8, 8))
plt.pie(quarterly_summary['Amount'], labels=quarterly_summary['Quarter'].astype(str), autopct='%1.1f%%', startangle=140)
plt.title('Income and Expense Ratio by Quarter')
plt.show()




# Create pie chart for expense categories
plt.figure(figsize=(8,8))
# Filter out zero values and ensure we have valid data

valid_expenses = expense_by_category[expense_by_category['Total_Amount'] > 0]
if not valid_expenses.empty:
    plt.pie(valid_expenses['Total_Amount'], 
            labels=valid_expenses['Category'], 
            autopct='%1.1f%%', 
            startangle=140,
            colors=plt.cm.Set3.colors)
    plt.title('Expense Distribution by Category')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
else:
    print("No valid expense data to display in pie chart")
# Create bar charts for category analysis   
plt.figure(figsize=(12,6))
sns.barplot(x='Category', y='Total_Amount', data=expense_by_category, hue='Category', palette='viridis', legend=False)
plt.title('Total Expenses by Category')
plt.xlabel('Category')
plt.ylabel('Total Amount')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Create income source visualization
plt.figure(figsize=(12,6))
sns.barplot(x='Source', y='Total_Amount', data=income_sources, hue='Source', palette='plasma', legend=False)
plt.title('Total Income by Source')
plt.xlabel('Income Source')
plt.ylabel('Total Amount')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Create pie chart for income sources
plt.figure(figsize=(8,8))
plt.pie(income_sources['Total_Amount'], labels=income_sources['Source'], autopct='%1.1f%%', startangle=140)
plt.title('Income Distribution by Source')
plt.axis('equal')
plt.show()      
