#packages
import pandas as pd
from pathlib import Path

#set data directory
images_path = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
data_path = '/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/VEA study - tasks for students/SOCKS project/CH Corpus/CHB_corpus_master.xlsx' #finish path to excel spreadsheet

#extract num_panels from data_path
#TODO: not working, not sure why not - doesn't think "Panel #" is a column name
num_panels = pd.read_excel(data_path, usecols="Panel #")

print(list(num_panels.columns.values))

#print(num_panels[1])

for comic_num in len(images_path.iterdir()):
    #pair comics with num_panels
    continue
    #use CNN for embedding

    #what backbone for output?

    #MSE for optimization
