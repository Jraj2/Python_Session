#List program

student =["Jaya",98,9.99]
print(student[2])

#edit list
student[2] = 8.78
print(student)

# create a similar string and try to edit it
str = "Jaya,98,9.99"
print(str[4])

# do slicing of the list
print(student[0:2]) # prints elements from index 0 to 1
print(student[0:3])     # prints characters from index 0 to 3

# negative slicing
print(student[-3:-1])   # prints elements from index -3 to -2

# use append() to add an element to the list
student.append("A+")
print(student)

# create new list of marks
student_marks = [98, 95, 88, 76]
print(student_marks)

# use sort() to sort the list
student_marks.sort()
print(student_marks)
student_marks.reverse()
print(student_marks)

student_marks.insert(3,66)
print(student_marks)

student_marks.sort(reverse=True)
print(student_marks)

print(student_marks.sort(reverse=True))
print(student_marks)


# list methods
list1 = ["bananas", "apples", "oranges"]
print(list1.sort(reverse=True))
print(list1)

# tuple methods
tuple1 = (10,33,56,21,10,10)
print(type(tuple1))
print(tuple1.count(10))
print(tuple1.index(56))

# WAP to create a list of 5 of your favorite movies and perform the following operations:
Movielist = []
movie1=input("Enter the name of your favorite movie 1: ")
Movielist.append(movie1)
movie2=input("Enter the name of your favorite movie 2: ")
Movielist.append(movie2)
movie3=input("Enter the name of your favorite movie 3: ")
Movielist.append(movie3)
print("Movies List: ",Movielist)

# Another method to create list
Movielist.append(input("Enter the name of your favorite movie 4: "))
print("Movies List: ",Movielist)

# WAP to check whether string is palindrome or not

list5 = ["madam"]
str2 = list5.copy()
print(str2)
str2.reverse()
if list5 == str2:
    print("The string is a palindrome")
else:
    print("The string is not a palindrome")