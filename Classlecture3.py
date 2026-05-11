#Write a program to create an Account class with methods to deposit, withdraw, and print balance

class Account:
    balance = 0.0
    acc_num = "10067891234"

    def acc_debit(self,amount): 
        if amount > self.balance:
            print("Insufficient balance")
        else:
            self.balance -= amount
            print(f"Debited {amount}. New balance is {self.balance}")
    
    def acc_credit(self,amount):
        self.balance += amount
        print(f"Credited {amount}. New balance is {self.balance}")
        #self.print_balance(self.balance)

    def print_balance(self):
        print(f"Current balance is {self.balance}")

account1 = Account()
account1.acc_num = "123456789"  
account1.acc_credit(500.0)
account1.acc_debit(200.0)
account1.print_balance()

""" Deleting the account object or class attribute
del account1
print("Account object deleted")
print(account1)
print(Account.acc_num)"""

print("Account class attribute 'acc_num' deleting...")
print(Account.acc_num)
del Account.acc_num
print("Account class attribute 'acc_num' deleted")
print(Account.acc_num)