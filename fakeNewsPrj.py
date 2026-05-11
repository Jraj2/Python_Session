import random


fakeList1 =["Jaya","Shilpa","Archana","Anant"]
fakeList2=[" is roaming with "," is riding "," laughing out with "," enjoying icecream with "]
fakeList3 =["goat","buffalo","tiger","elephant"]

while True:
    print("Fake News begin....\n")
    str1 = random.choice(fakeList1)
    str2 = random.choice(fakeList2)
    str3 = random.choice(fakeList3)

    print(str1 + str2 + str3)
    user_choice= input("Want to continue(y/n) ?").lower()
    if user_choice =='n':
        break
