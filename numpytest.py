import numpy as np

# Create a 1-dimensional NumPy array from a Python list
arr1d = np.array([1, 2, 3, 4, 5])
print("1D Array:", arr1d)
print("Type of arr1d:", type(arr1d))
print("Shape of arr1d:", arr1d.shape)
print("Number of dimensions of arr1d:", arr1d.ndim)

# Create a 2-dimensional NumPy array (matrix)
arr2d = np.array([[10, 11, 12], [13, 14, 15]])
print("\n2D Array:\n", arr2d)
print("Shape of arr2d:", arr2d.shape)
print("Number of dimensions of arr2d:", arr2d.ndim)

# Create an array filled with zeros
zeros_array = np.zeros((3, 4))
print("\nArray of Zeros:\n", zeros_array)

# Create an array filled with ones
ones_array = np.ones((2, 2))
print("\nArray of Ones:\n", ones_array)

# Create an array with a range of values
range_array = np.arange(0, 10, 2) # Start, Stop (exclusive), Step
print("\nRange Array:", range_array)

# Reshaping an array
reshaped_array = np.arange(1, 7).reshape(2, 3)
print("\nReshaped Array (2x3):\n", reshaped_array)

# Basic array operations
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("\nElement-wise addition:", a + b)
print("Element-wise multiplication:", a * b)