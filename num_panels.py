#packages
import pandas as pd
from pathlib import Path

#set data directory
images_path = Path('~/Library/CloudStorage/OneDrive - University of Vermont/VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
data_path = '~/Library/CloudStorage/OneDrive - University of Vermont/VEA study - tasks for students/SOCKS project/CH Corpus/CHB_corpus_master.xlsx' #finish path to excel spreadsheet

#extract num_panels from data_path
num_panels = pd.read_excel(data_path, usecols='Panel #')

for comic_num in len(images_path.iterdir()):
    #pair comics with num_panels

    #use CNN for embedding
    
    #what backbone for output?

    #MSE for optimization
