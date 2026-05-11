
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# Create pie chart for expense categories
plt.figure(figsize=(8,8))
# Filter out zero values and ensure we have valid data

#valid_expenses = category_expenses[category_expenses['Total_Amount'] > 0]
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
sns.barplot(x='Category', y='Total_Amount', data=category_expenses, hue='Category', palette='viridis', legend=False)
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
