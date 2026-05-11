"""import numpy as np  
import pandas as pd

data = pd.read_csv('data.csv')"""

# String Example

str = "sanjeevini Srushti"
print(str[7])  # Output: v

#Try to edit value of any index, will throw error
#str[10] = '*'  # This will raise a TypeError
print(str)

#Example of slicing
print(str[0:9])  # Output: Sanjeevin
print(str[5:])  # Output: Srushti
print(str[0:len(str)])  # Output: Sanjeevini Srushti
print(str[:9])

# use capitalize() function
print(str.capitalize())  # Output: Sanjeevini srushti
print(str.find('r'))  # Output: 10
str1 ="hi $I am the $ symbol and $price is $100"
print(str1.count('$'))  # Output: 4