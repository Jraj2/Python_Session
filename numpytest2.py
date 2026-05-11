import numpy as np
#create a regular list
my_list = [10, 20, 30, 40, 50]
my_list2 = [[60, 70, 80],[ 90, 100,80]]
print("Regular List:", my_list)
print("Type of my_list:", type(my_list))

#convert the list to a numpy array
my_array = np.array(my_list)
print("\nNumpy Array:", my_array)
print("Type of my_array:", type(my_array))

print(my_array +5)
my_array = np.array(my_list)
my_array2 = np.array(my_list2)
print(my_array.ndim)
print(my_array2.ndim)

print("Shape of my_array:", my_array.shape)
print("Shape of my_array2:", my_array2.shape)

print(my_array.size)
print(my_array2.size)