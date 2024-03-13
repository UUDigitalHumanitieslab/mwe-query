import pandas as pd
from pivottablejs import pivot_ui
from IPython.display import HTML

datafilename = './pivotdata/mps.csv'

data = pd.read_csv(datafilename)

pivot_ui(data)