import pandas as pd
from io import StringIO

with open("data.csv", "r") as f:
    data = f.read()
data = StringIO(data)
df = pd.read_csv(data)
df = df.drop_duplicates()
if df.empty != True:
    print(f"Successfully removed duplicate rows.")
df.to_csv("data.csv")