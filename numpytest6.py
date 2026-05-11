# Removal of element using delete method
#np.delete(array_name,index,axis=None)
import numpy as np
array1 = np.array([1,2,3,4,5,6,7,8])
print("Before Deletion",array1)

#delete element at 3rd index position

array_del = np.delete(array1,3,axis=0)
print("Element after deletion from 1D array",array_del)
array_2D = np.array([[2,3,4,5],[6,7,8,9]])
new_array2d_del = np.delete(array_2D, 0, axis=0)
print("Element after deletion from 2D array",new_array2d_del)

#Spliting array
print("Before spliting array:",array1)
print(np.split(array1,2)) # Split array in 2 parts

print(np.vsplit(array_2D),2)



