import numpy as np
import pandas as pd
#Customer dataframe

df_CustomerR1 = pd.DataFrame({
    'CustomerId':[101,102,103,104],
    'Name':['Ramesh','Suresh','Kalpesh','Giresh']
})

df_CustomerR2 = pd.DataFrame({
    'CustomerId':[105,106,107,108],
    'Name':['Ramesh','Suresh','Kalpesh','Giresh']
})

df_concat = pd.concat([df_CustomerR1,df_CustomerR2],axis=0, ignore_index= True)
print(df_concat)
