class Person:
    name = "anonymous"

    @classmethod
    def change_name(cls,new_name):
        cls.name = new_name

person1 = Person()

person1.change_name("Alice")
print(person1.name)  # Output: Alice
print(Person.name)  # Output: anonymous


# Demonstrate the use of @property decorator
class Student:
    def __init__(self,phy,chem,maths):
        self.phy = phy
        self.chem = chem    
        self.maths = maths

    @property
    def percentage(self):
            return  str((self.phy + self.chem + self.maths) / 3) + "%"

studenet1 = Student(90,80,70)
print(studenet1.percentage) 
studenet1.phy = 95
print(studenet1.percentage)  # Output: 80.0%