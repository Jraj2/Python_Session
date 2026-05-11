class Car:
    color = "Red"
    model = "Sedan"
    year = 2020
    name = ""

    def __init__(self, fullname):
        print("Car object created")
        self.name = fullname
        print(self.name)

s1 = Car("Maruti Suzuki");
#print(s1.color)
#print(s1.model)     
#print(s1.year)  
print(s1)
