import matplotlib.pyplot as plt
x=[3,4,5,6]
y =[30,40,50,60]

plt.subplot(1,2,1) #1st row, 2nd column and 3rd position
plt.plot(x,y)
plt.title('Line Chart')

plt.subplot(1,2,2) # side by side new plot
plt.bar(x,y)
plt.title("Bar Chart")

plt.tight_layout()
plt.show()

