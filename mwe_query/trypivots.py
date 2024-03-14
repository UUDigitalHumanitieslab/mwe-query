import pandas as pd
from pivottablejs import pivot_ui

datafilename = "./pivotdata/mps.csv"

data = pd.read_csv(datafilename)

pivot_ui(data)
