#Create a list
mylist= []
print("Initial blank list: ")
print(mylist)

#Adding elements to the list
mylist.append("Dressing Table")
mylist.append("Dinning Table")
mylist.append("Sofa Set")
mylist.append("Shoe rack")

#Printing the elements of the list
print("\nList after adding elements: ")
print(mylist)

#Accessing elements of the list
print("\nAccessing second element of the list: ")    
print(mylist[1])


#Add new list of items into the existing list

new_items = ["Bed", "Wardrobe"]
mynewlist = mylist + new_items
print("\nList after adding new items: ")
print(mynewlist)
print("old list remains the same:", mylist)

#Replace Bed with Study Table as list is mutable(changeable)
mynewlist[4] = "Study Table"
print("\nList after replacing Bed with Study Table: ")
print(mynewlist)

# Demo programme

# Rahul's initial grocery inventory (created with items already in it)
items = ["Milk", "Eggs", "Bread"]
print("Initial inventory:", items)

# New items arrive - add them to the inventory
items.append("Butter")
print("After adding Butter:", items)

items.append("Cheese")
print("After adding Cheese:", items)

print("=" * 50)  # Separator line for clarity

# BONUS: List Concatenation (joining two lists)
# Rahul has two separate lists of numbers he wants to combine
numbers = [10, 20, 30]              # First list
new_numbers = [40, 50, 60]          # Second list

# Using the + operator to concatenate (join) lists
combined_numbers = numbers + new_numbers
print("Original numbers:", numbers)
print("New numbers:", new_numbers)  
print("Combined list:", combined_numbers)