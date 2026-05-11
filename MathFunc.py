import math
from datetime import datetime as dst
import statistics
import numpy as np

print("Value of Pi:", math.pi)
print("Square root of 16:", math.sqrt(16))
print("Factorial of 5:", math.factorial(5))
current_date = dst.now()
print("Current Date and Time:", current_date)

score = [88, 92, 79, 93, 85]
print("Mean of scores:", statistics.mean(score))
print("Median of scores:", statistics.median(score))