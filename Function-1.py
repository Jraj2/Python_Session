# write a function to do sum of 3 numbers and then calculate average of those numbers

def sum_avg(num1,num2,num3):
    total_sum = num1 + num2 +num3
    print("Sum of three numbers:", total_sum)
    average = total_sum / 3
    print("Average of three numbers:", average)

# input numbers from users
number1 = float(input("Enter first number: "))
number2 = float(input("Enter second number: "))
number3 = float(input("Enter third number: "))  
sum_avg(number1, number2, number3)

# write a function to print length of list

def list_length(input_list):
    length = len(input_list)
    print("Length of the list:", length) 
    print("List elements are:", input_list, end="")   

# input list from user
user_list1 = [1, 2, 3, 4, 5]
user_list2 = ["a", "b", "c"]
list_length(user_list1)
list_length(user_list2)

# WAF to find the factorial of a number

def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
    
fnum = int(input("Enter a number to find its factorial: "))
result = factorial(fnum)
print(f"Factorial of {fnum} is: {result}")

#WAF to convert USD to INR
def usd_to_inr(usd):
    conversion_rate = 88.0  # Example conversion rate
    inr = usd * conversion_rate
    return inr

usd_amount=float(input("Enter amount in USD: "))
inr_amount = usd_to_inr(usd_amount)
print(f"{usd_amount} USD is equal to {inr_amount} INR")


# WAF to check whether a number is even or odd
def check_odd_even(num):
    if num %2 ==0 :
        print(f"{num} is an Even number")
    else:
        print(f"{num} is an Odd number")

number = int(input("enter a number to check even or odd: "))
check_odd_even(number)