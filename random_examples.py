import random

# 1. Basic random number generation
print("1. Basic Random Numbers:")
# Random float between 0.0 and 1.0
print("Random float (0 to 1):", random.random())
# Random integer between two numbers (inclusive)
print("Random integer (1 to 6):", random.randint(1, 6))
# Random float within a range
print("Random float (10 to 20):", random.uniform(10, 20))

# 2. Making random choices
print("\n2. Random Choices:")
# List of items
fruits = ['apple', 'banana', 'orange', 'grape', 'mango']
# Choose one random item
print("Random fruit:", random.choice(fruits))
# Choose multiple random items (with replacement)
print("3 random fruits (can repeat):", random.choices(fruits, k=3))
# Choose multiple random items (without replacement)
print("3 random fruits (no repeats):", random.sample(fruits, k=3))

# 3. Shuffling sequences
print("\n3. Shuffling:")
# Create a list of numbers
numbers = list(range(1, 11))  # numbers 1 to 10
print("Original list:", numbers)
# Shuffle the list
random.shuffle(numbers)
print("Shuffled list:", numbers)

# 4. Random with weights
print("\n4. Weighted Random Choices:")
colors = ['red', 'blue', 'green']
weights = [0.6, 0.3, 0.1]  # 60% red, 30% blue, 10% green
print("Weighted choice:", random.choices(colors, weights=weights, k=1)[0])

# 5. Simulating dice rolls
print("\n5. Dice Rolling Simulation:")
def roll_dice(num_dice=1, sides=6):
    """Roll multiple dice and return their results"""
    return [random.randint(1, sides) for _ in range(num_dice)]

# Roll one die
print("Single die roll:", roll_dice(1)[0])
# Roll multiple dice
print("Rolling 3 dice:", roll_dice(3))

# 6. Random for games
print("\n6. Game Examples:")
# Coin flip
coin = random.choice(['Heads', 'Tails'])
print("Coin flip:", coin)

# Card deck
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
# Draw a random card
card = f"{random.choice(ranks)} of {random.choice(suits)}"
print("Random card:", card)

# 7. Setting random seed (for reproducibility)
print("\n7. Using Random Seed:")
# Set a specific seed
random.seed(42)
print("Random number with seed 42:", random.random())
# Same seed will give same random number
random.seed(42)
print("Random number again with seed 42:", random.random())

# 8. Generate random password
print("\n8. Random Password Generator:")
def generate_password(length=8):
    """Generate a random password"""
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
    return ''.join(random.choice(characters) for _ in range(length))

print("Random 8-character password:", generate_password())
print("Random 12-character password:", generate_password(12))