class Car:
    @staticmethod   
    def start():
        print("car started...")

    @staticmethod
    def stop():
        print("car stopped...")

class ToyotaCar(Car):
    def __init__(self,name):
        self.name = name

class FortunerCar(Car):
    def __init__(self,name):
        self.name = name

toyotaobj = ToyotaCar("Toyota Corolla")
print(toyotaobj.name)
toyotaobj.start()  # This will raise an AttributeError
toyotaobj.stop()   # This will raise an AttributeError

fortunerobj = FortunerCar("Toyota Fortuner")
print(fortunerobj.name)
fortunerobj.start()  # This will raise an AttributeError
fortunerobj.stop()   # This will raise an AttributeError