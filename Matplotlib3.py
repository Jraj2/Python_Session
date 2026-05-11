import matplotlib.pyplot as plt
hours_studies=[1,2,3,4,5,6,7,8]
exam_score = [50,60,70,75,80,85,90,95]
plt.scatter(hours_studies,exam_score,color='green',marker='^',label='Student Data')
plt.xlabel("Hours Studied")
plt.ylabel("Exam Score")
plt.title("Relationship B/W Study Time and Exam Score")
plt.legend("lower right")
plt.grid(True)
plt.show()

# Comparison of 2 section of class
plt.scatter([1,2,3,4],[50,60,70,80],color ='blue', label='Section A')
plt.scatter([1,2,3,4],[79,89,99,59],color ='orange', label='Section A')
#plt.scatter(hours_studies,exam_score,color='green',marker='o',label='Student Data')
plt.xlabel("Hours Studied")
plt.ylabel("Exam Score")
plt.title("Comparison of Two Section")
plt.legend("lower right")
plt.grid(True)
plt.show()