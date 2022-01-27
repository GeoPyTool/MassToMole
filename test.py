import pandas as pd
import chempy,os

LocationOfMySelf = os.path.dirname(__file__)
DataFileInput= LocationOfMySelf +"./test.csv"
raw = pd.read_csv(DataFileInput, engine='python')

print(raw.index,raw.columns.tolist())