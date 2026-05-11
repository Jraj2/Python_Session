#WAP to create a class Account which have private attribute account password

class Account:
    __password = "admin123"  # private attribute
    acc_number = "10067891234"

    def __init__(self,acc_number,acc_password):
        self.acc_number = acc_number
        self.__password = acc_password
        
    def print_acc_info(self):
        print(f"Account Number: {self.acc_number}")
        print(f"Account Password: {self.__password}")

account1 = Account("123456789","admin333")
account1.print_acc_info()
print(account1.acc_number)
print(account1.__password)  # Accessing private attribute using name mangling

    