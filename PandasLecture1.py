import numpy as np
import pandas as pd

# program to save dictionary data into .csv file
data={"Name":['Jaya','Raj','Deepa'],
      "Age":[39,39,39],
      "city":["Bangalore","Delhi","Bombay"]}
print(data)
df=pd.DataFrame(data)
print(df)
#df.describe()
#print(df)
#save the file in csv format after ignoring index
df.to_csv("output.csv",index=False)
print(df.head(7)) #Display 7 rows from top
print(df.tail(3)) # Display 3 rows of last
print(df.info())
print(df.shape())
print(df.columns)
#df.to_excel("output.xlsx",index=False)
#df.to_json("output.json",index=False)

#Read csv file
data1 = pd.read_csv('Employee_details.csv')
print(data1.head(10)) #display top 10 row
print(data1.tail(4)) #display bottom 4 row

# info() method give concise summary of the data-- rows,columns,data type,non null count, memory usage of datafram

data2 = pd.read_json("sample_Data.json")
print("Display data information")
data2.info()