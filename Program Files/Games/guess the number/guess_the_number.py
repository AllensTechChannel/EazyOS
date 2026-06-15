import random

number = random.randint(1, 100)
attempts = 0

print("Welcome to Guess the Number! Guess a number from 1-100")
print("-" * 25)

while True:
    guess = int(input("Your guess: "))
    attempts += 1
    
    if guess < number:
        print("Too low!")
    elif guess > number:
        print("Too high!")
    else:
        print(f"Correct! You got it in {attempts} attempts.")
        break
