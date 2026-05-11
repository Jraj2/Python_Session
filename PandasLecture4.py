# Interpolate use in time and series kind of problem to fill the estimated value for missing cells in dataset
import pandas as pd
import numpy as np

# Create sample data with missing values
data = {
    "Time":[1,2,3,4,5],
    "Value":[10,None,30,None,50]
}

df = pd.DataFrame(data)
print("Before Inetrpolation")
print(df)

#use column where we want to make changes

df['Value'] = df['Value'].interpolate(method ="linear")
print("After Inetrpolation")
print(df)

# Show the type of interpolation that occurred
#print("\nExplanation of interpolated values:")
#print("- Between Time 1 and 4: Linear interpolation estimated the missing value")
#print("- Between Time 4 and 6: Linear interpolation estimated the missing value")