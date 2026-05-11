import numpy as np
zeros_list = np.zeros((2,3)) #aray list filled with zeroes
print(zeros_list)

one_list = np.ones((3,5))  #array list filled with ones
print(one_list)

default_list = np.full((3,4),8) # array list filles with initial value 8
print(default_list)

# print list of sequence array step by 2 and start from 1 and end with 10

arra_seq = np.arange(1,10,2)
print(arra_seq)

identity_matrix = np.eye(3,3) # print diagonal vale as 1 and rest as 0
print(identity_matrix)

#check the shape,size and dimension of array list
array_list2 =np.array([[2,3.0],[3,6],[4,7.0]])

print(array_list2.shape)

#print size which is total number of elements
print(array_list2.size)

#print dimension of array list
print(array_list2.ndim)

#print type of array list before conversion
print(array_list2.dtype)

#print array list element
print(array_list2)

#print type of numpy array after conversion
array_list3 =array_list2.astype(int)
print(array_list3)
print(array_list3.dtype)

# Aggregration and Mean of numpy array

array_list4 =np.sum(array_list3)
print(array_list4)

# min max sd mean 