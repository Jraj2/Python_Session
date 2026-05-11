import numpy as np
import random

ROCK ='r'
SCISSORS ='s'
PAPER ='p'

emojis = {'r':"🪨",'s':"✂️",'p':"📄"}
#valid_choices=('r','p','s') 
# Another way to use dictionary value
valid_choices=tuple(emojis.keys())

def get_users_choice():
    while True:
        user_choice = input("Rock, paper, or scissors? (r/p/s)?")
        if user_choice  in valid_choices:
            return user_choice
            
        else:
            print("Invalid Choice")

def display_choices(user_choice,comp_choice):
    print(f'You chose {emojis[user_choice]}')
    print(f'Computer chose {emojis[comp_choice]}')

def determine_winner(user_choice,comp_choice):
    if user_choice == comp_choice :
        print("Tie!")
    elif (user_choice =='ROCK' and comp_choice =='SCISSORS') or (user_choice =='SCISSORS' and comp_choice =='PAPER') or (user_choice =='PAPER' and comp_choice =='ROCK'):
        print("You win")
    else :
        print('You loose')


def play_game():
    while True:
        user_choice1 = get_users_choice()
        comp_choice =random.choice(valid_choices)

        display_choices(user_choice1,comp_choice)
        determine_winner(user_choice1,comp_choice)

        should_continue = input("Continue? (y/n):")
        if(should_continue=='n'):
         break

play_game()