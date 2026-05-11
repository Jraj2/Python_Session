import numpy as np
#broadcasting
arr1 = np.array([[2,3,4],[4,5,6]])
arr2 = np.array([10])
print(arr1+arr2)

# Handling missing values 
#isnan() nan_to_num() 

array1 = np.array([1,2,3,np.nan,5,6,np.nan])
print(array1)
print(np.isnan(array1))

cleaned_array =np.nan_to_num(array1,nan=100)
print(cleaned_array)

array2= np.array([1,2,3,np.inf,5,-np.inf,6])
print(np.isinf(array2))
cleaned_arra2 = np.nan_to_num(array2,posinf=1000,neginf=-1000)
print(cleaned_arra2)