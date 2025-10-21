# Example of dictionary in Python
student_ages = {"Alice": 20, "Bob": 22, "Charlie": 19}
print(student_ages)

# Example of 2nd dictionary set in python
student_ages1 = {"Jaya": 38,"Maa": 67}
print(student_ages1)

# Include list and tuple in a  dictionary
student_info = {
    "name": "Jaya",
    77: ["Jaya", "Ravi", "Anita"],
    "grades_tuple": (98, 95, 88),
    55.5:78}
print(student_info)
print(type(student_info))
student_info["name"] = "Jaya Raj"
print(student_info)

#Add new key-value pair
student_info["Age"] = 38
print(student_info)

# create a null dictionary and add elements to it
empty_dict ={}
empty_dict["City"] = "Bangalore"
print(empty_dict)