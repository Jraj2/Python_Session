import numpy as np
import pandas as pd
import random

while True:
    user_input = input("Roll the dice? (y/n)").lower()
#print("User choice", user_input)

    if (user_input =='y'):
        print("User choice", user_input)
    #num_arr =[1,2,3,4,5,6]
        rnd_num1=(random.randint(1,6))
        rnd_num2=(random.randint(1,6))
        print(f'({rnd_num1},{rnd_num2})')
    #print(rnd_num+1 ,random.randint(0,5))

    elif (user_input =='n'):
        print("Thanks For Playing !")
        break
    else :
     print("Invalid Choice!")

    
    
    