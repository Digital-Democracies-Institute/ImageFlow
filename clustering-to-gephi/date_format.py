import pandas as pd


df = pd.read_csv("all_metadata.csv")
#
# df['time_new']
#
# df = pd.to_.time(df['time_new'])

df['updated_datetime'] = pd.to_datetime(df['time_new'], format='%H:%M')

print(df)