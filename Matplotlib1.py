import matplotlib.pyplot as plt
x =['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec']  #horizontal x axis
y=[10,15,7,20,12,25,30,40,20,30,30,50]  #vertical y axis

plt.plot(x,y,color='blue',linestyle='--',linewidth=2,marker='o',label='2025 Sales Data')
plt.title("Monthly Sales Data Report")
plt.xlim(0,12)
plt.ylim(0,50)
#plt.xticks([1,2,3,4,5],['M1','M2','M3','M4','M5'])
plt.xlabel ("Months")
plt.ylabel("Sales Per Month")
plt.legend(loc="lower right",fontsize=5)
plt.grid(color="gray",linestyle=':',linewidth=1)
plt.show()