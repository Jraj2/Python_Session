import numpy as np
import pandas as pd
import random

counter = True
int_num1 = random.randint(1,100)
print(int_num1)
try:
    while counter:
        int_num2 = input("Guess the number between 1 and 100 :")
        if int_num2.isdigit:
            if int(int_num2) > int_num1:
                    print("Too high")
            elif int(int_num2) < int_num1:
                    print("Too low")
            elif int(int_num2) ==int_num1:
                    print("Congratulations! You guessed the number.")
                    counter = False
                    
except ValueError:
    print("Please enter a valid number")
    
finally:    
    print(int_num1)
    print(int_num2)



