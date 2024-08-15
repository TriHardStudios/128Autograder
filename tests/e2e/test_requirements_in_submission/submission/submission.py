import matplotlib
import matplotlib.pyplot as plt

print(f"OUTPUT {matplotlib.__version__}")

plt.plot([1, 2, 3, 4], [1, 4, 9, 16])

plt.savefig("plt.png")
