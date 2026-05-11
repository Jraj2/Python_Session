# Python OR operator examples

# 1. Basic OR operator (|) for boolean values
x = True
y = False
result1 = x or y  # Returns True because at least one value is True
print("1. Basic OR:", result1)

# 2. Multiple conditions with OR
age = 25
income = 50000
is_eligible = age > 18 or income > 40000  # Returns True if either condition is met
print("2. Multiple conditions:", is_eligible)

# 3. OR in if statements
temperature = 85

if temperature <= 60 or temperature >= 80:
    print("3. Warning: Temperature is uncomfortable!")

# 4. Short-circuit evaluation
# OR returns the first True value it finds
first_true = "Yes" or "Maybe" or "No"  # Returns "Yes"
all_false = 0 or "" or None or False  # Returns False
print("4. Short-circuit results:", first_true, ",", all_false)

# 5. OR with comparison operators
grade = 75
if grade < 60 or grade > 100:
    print("5. Invalid grade!")
else:
    print("5. Valid grade!")

# 6. Combining AND and OR
has_ticket = True
is_vip = False
has_invitation = True

can_enter = (has_ticket or has_invitation) and not is_vip
print("6. Can enter event:", can_enter)

# 7. OR in list comprehension
numbers = [1, 2, 3, 4, 5]
evens_or_threes = [n for n in numbers if n % 2 == 0 or n % 3 == 0]
print("7. Numbers that are even OR divisible by 3:", evens_or_threes)

# 8. Using OR for default values
user_name = "" or "Guest"  # If user_name is empty, use "Guest"
print("8. Username:", user_name)

# 9. Bitwise OR operator (|)
# Binary: 5 = 101, 3 = 011
bitwise_result = 5 | 3  # Result: 7 (111 in binary)
print("9. Bitwise OR of 5 | 3:", bitwise_result)

# 10. OR in set operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
union_set = set1 | set2  # Same as set1.union(set2)
print("10. Union of sets:", union_set)