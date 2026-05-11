#WAP to create class of student and should print average of 3 subjects marks
class Student_dtl:
    name = ""
    sub_marks =[]
    sum=0
    average=0

    @staticmethod #decorator
    def welcome_msg():
        print("Welcome to Student Average Calculator")

    def __init__(self,name,sub_marks):
        print("Student object created")
        self.name = name
        self.sub_marks = sub_marks
        

    def calculate_average(self):
        for mark in self.sub_marks:
            self.sum += mark
            print(f"Name:{self.name}, your average score is : {self.sum/len(self.sub_marks)}")


Student_dtl.welcome_msg()
student1 = Student_dtl("John Doe",[85,90,78])
student1.calculate_average()
student2 = Student_dtl("Jane Smith",[92,88,95])
student2.calculate_average()

