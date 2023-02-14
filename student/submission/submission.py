
if __name__ == "__main__":

    print("1. Addition\n2. Subtraction\n3. Multiplcation 4. Integer Division\n5. Division")


    mode = input("MODE> ")

    number1 = float(input("NUMBER 1> "))
    number2 = float(input("NUMBER 2> "))

    result = 0;

    if mode == "1":
        result = number1 + number2

    elif mode == "2":
        result = number1 - number2

    elif mode == "3":
        result = number1 * number2

    elif mode == "4":
        result = number1 // number2

    elif mode == "5":
        result = f"{number1 / number2:.02f}"


    print(f"OUTPUT {result}")
