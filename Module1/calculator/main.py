# Operation Functions
def add(num1, num2):
    return num1 + num2

def subtract(num1, num2):
    return num1 - num2

def multiply(num1, num2):
    return num1 * num2

def divide(num1, num2):
    if num2 == 0:
        print("Error: Division by zero")
        return ""
    return num1 / num2


# Simple calculator funtion
def calculator():
    while True:
        # Printing options for the user
        print("\n\nCalculator")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Exit")

        # Taking users input
        userInput = str(input("\nSelect Operation (1/2/3/4/5): "))

        # IF the user selected 5 will exit the script
        if userInput == '5':
            print("\nExiting calculator. Goodbye!")
            break
        # Check if user has entered valid input
        if userInput in ['1', '2', '3', '4']:
            try:
                num1 = float(input("\nEnter first number: "))
                num2 = float(input("Enter second number: "))
                
                result = ""

                if userInput == '1':
                    result = add(num1, num2)
                elif userInput == '2':
                    result = subtract(num1, num2)
                elif userInput == '3':
                    result = multiply(num1, num2)
                elif userInput == '4':
                    result = divide(num1, num2)
                
                if(result != ""):
                    print("Result: ", result)

            except ValueError:
                print("\nInvalid input! Please enter numbers only.")
        else:
            print("\nInvalid option!")
# END of calculator function

# Calling Calulcator fun
calculator()