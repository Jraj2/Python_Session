import matplotlib.pyplot as plt


#fig, ax = plt.subplots(nrows,ncols, figsize=(width,height))
fig, ax =plt.subplots(1,2, figsize=(10,5))
x=[34,44,57,67]
y =[30,40,35,65]

ax[0].plot(x,y, color='blue')
ax[0].set_title('Line Plot')

ax[1].bar(x,y, color ='green')
ax[1].set_title('Bar Chart')
plt.tight_layout()
fig.suptitle("Comparison of Plot and Bar Chat")
plt.savefig('line_plot.png', dpi=300, bbox_inches='tight')
plt.show()