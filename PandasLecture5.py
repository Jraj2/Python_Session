import numpy as np
import pandas as pd
#Customer dataframe

df_Customer = pd.DataFrame({
    'CustomerId':[101,102,103,104],
    'Name':['Ramesh','Suresh','Kalpesh','Giresh']
})

#Order Dataframe
df_Order = pd.DataFrame({
    'CustomerId':[101,102,103,105],
    'OrderAmount':[250,560,670,334]
})

#Apply Merge using inner join concept
df_merged = pd.merge(df_Customer,df_Order,on="CustomerId",how="inner")
print("Inner Join")
print(df_merged)

#Apply Merge using outer join concept
df_merged1 = pd.merge(df_Customer,df_Order,on="CustomerId",how="outer")
print("Outer Join")
print(df_merged1)

#Apply Merge using left join concept
df_merged2 = pd.merge(df_Customer,df_Order,on="CustomerId",how="left")
print("left Join")
print(df_merged2)

#Apply Merge using right join concept
df_merged3 = pd.merge(df_Customer,df_Order,on="CustomerId",how="right")
print("Right Join")
print(df_merged3)

#Apply Merge using cross join concept
df_merged4 = pd.merge(df_Customer,df_Order,how="cross")
print("Cross Join")
print(df_merged4)

