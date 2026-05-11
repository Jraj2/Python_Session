# search for the number x in given tuple using while loop
tuple1=(10,20,30,40,50,60,70,80,90,100)
num=int(input("Enter a number to search in the tuple: ")) 
length=len(tuple1)
print("length of tuple is:",length)
found=False
m=0
while m<length:
    print("within while loop")
    if tuple1[m]==num:
        #print(tuple1[m])
        found=True
        print("element found at index:",m)
        break
    m+=1
print("value of m is:",m)

# for loop to print elements of a list
List1=[2,4,6,8,10,12,14,16,18,20]
for element in List1:
    print(element)

for i in range(len(List1)):
    print("Element at index",i,"is",List1[i])