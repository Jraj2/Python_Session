#Code to test to take action based on traffic light color
traffic_light = input("Enter the traffic light color (red, yellow, green): ")
if traffic_light == "red":
    print("Stop")
elif traffic_light == "yellow":
    print("Get Ready")
elif traffic_light == "green":  
    print("Go")
else:
    print("Traffic light is broken")


 # Single line if / ternary operator
food = input("Enter the food you want to eat: ") 
eat = "Yes" if food == "Pizza" else "No"
print("Do you want to eat Pizza?", eat)
# End of the code

#Type casting

num1 =int("7")
num2 = 8
sum = num1 + num2
print("type of num1:", type(num1))
print("Sum without type casting:", sum)  # This will concatenate as string


