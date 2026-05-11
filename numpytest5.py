import numpy as np
array_1D = np.array([2,3,4,5,6])
print("Before insertion", array_1D)
print(array_1D)

#insert new elemnt at 3rd position
array_new_1D= np.insert(array_1D,2,100)
print("After insertion", array_new_1D)

#insert new element for 2D array
array_2D = np.array([[2,3],[4,5]])
print("Before insertion",array_2D)

array_new_2D = np.insert(array_2D,1,[100,200],axis=1)

print("After insertion into",array_new_2D)

# if use axis = None it will flatten the array

array_new_2D_axis = np.insert(array_2D,1,[100,200],axis=None)
print(array_new_2D_axis)

# Add element at the end using append
#Before append
print("Before append",array_1D)
array_1D_app = np.append(array_1D,[77,88,99,22])
print("After append at the end",array_1D_app)

array_1D_1 = np.array([7,8,9,10,11])

array_1D_Merge = np.concatenate((array_1D,array_1D_1),axis =0)
print("After Merge rowise", array_1D_Merge)

array_1D_Merge = np.concatenate((array_1D,array_1D_1),axis =1)
print("After Merge columnwise", array_1D_Merge)