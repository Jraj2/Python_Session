import numpy as np

array_list = np.array([1,2,3,4,4,5,6,7,8,9,10,90,55,34,65])
print(array_list[0])
print(array_list[5])
print(array_list[-1]) # last element

#Slicing [start:stop:step]

print(array_list[1:5:1]) # will print from 1st index value  until stop -1
print(array_list[:3]) # will print from 0 index until 3-1
print(array_list[::-1]) # will print value in reverese order
print(array_list[::2]) # will print from 0th index until last step by 2

# Fancy indexing - selecting multiple elements in one go

print(array_list[[0,4,5]])

# Filtering Data / Boolen Masking retrieve data based on condition
# print element greater than 25
print(array_list[array_list>25])

# Reshaping and manipulating like converting 1D array into 2D without changing value of array. After conversion size of array will remain same
#reshape(rows,col) specify new shape

#print array before conversion

print("Before conversion********",array_list)
print("Size before conversion",array_list.size)
reshaped_array = array_list.reshape(5,3)
print("After conversion",reshaped_array)
print("Size after conversion",reshaped_array.size)

#ravel and flatten conver multidimensional array into 1D
multi_arr = np.array([[1,2,3,4],[5,6,7,8]])
print("Before conversion************",multi_arr)
print("After conversion************",multi_arr.flatten())
print(multi_arr)
print(multi_arr.ravel())
print("After conversion************",multi_arr.ravel())
