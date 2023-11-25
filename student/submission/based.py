mode = int(input())
n1, n2 = [float(i) for i in [input(), input()]]
print("OUTPUT", end=' ')
if mode == 1:
    r = n1 + n2
    print(f"{r:.0f}\r\n")
elif mode == 2:
    r = n1 - n2
    print(f"{r:.0f}\r\n")
elif mode == 3:
    r = n1 * n2
    print(f"{r:.0f}\r\n")
elif mode == 4:
    r = n1 // n2
    print(f"{r:.0f}\r\n")
elif mode == 5:
    r = n1 / n2
    print(f"{r:.2f}\r\n")


