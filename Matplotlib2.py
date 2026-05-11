import matplotlib.pyplot as plt
region=['North','South','East','West']
revenue = [3000,2000,1500,1000]
plt.pie(revenue, labels=region,autopct='%1.f%%', colors=['skyblue','gold','coral','lightgreen'])
plt.title ("Revenue Contribution By Region")
plt.show()

# print histogram ( use for numerical continuos data)
scores = [45,67,50,57,89,90,34,78,81,90,87,88,89,72,76,77,90]
plt.hist(scores, bins=5, color='coral',edgecolor='black')
plt.xlabel('Score Range')
plt.ylabel('Number Of Students')
plt.title('Score Distribution')
plt.show()
