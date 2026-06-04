import numpy as np
import pandas as pd
from pathlib import Path
from tensorflow.keras.utils import load_img, img_to_array
import tensorflow as tf
from tensorflow import keras
from PIL import Image

#-------------------------------------------------------------------------

best_model_path = Path(__file__).parent / "panel_counter_best.keras"
model = keras.models.load_model(best_model_path)

#-------------------------------------------------------------------------

#configuration of filepaths, image size for images of comics, size of batches for training, and number of epochs for training
IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
DATA_PATH = ('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
               'VEA study - tasks for students/SOCKS project/CH Corpus/CHB_corpus_master.xlsx')

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 50

#--------------------------------------------------------------------------

#Load labels of images and corresponding number of panels from excel spreadsheet
df = pd.read_excel(DATA_PATH)

FILENAME_COL = "Filename" #name of column with image filenames
PANEL_COL = "Panel #" #name of column holding number of panels

#throw out rest of columns and drop rows with no entries for either of these columns
df = df[[FILENAME_COL, PANEL_COL]].dropna()
#ensure that number of panels column holds integers
df[PANEL_COL] = df[PANEL_COL].astype(int)

#--------------------------------------------------------------------------

#Build dataset arrays
def load_image(filepath: Path) -> np.ndarray:
    img = load_img(filepath, target_size=IMG_SIZE)
    arr = img_to_array(img) / 255.0
    return arr

images = []
panel_nums = []
valid_rows = []

for _, row in df.iterrows():
    img_file = IMAGES_PATH / row[FILENAME_COL]
    if not img_file.exists():
        print(f"  [skip] not found: {img_file.name}")
        continue
    images.append(load_image(img_file))
    panel_nums.append(row[PANEL_COL])
    valid_rows.append(row)

X_img = np.array(images, dtype=np.float32) #image input to model
X_num = np.array(panel_nums, dtype=np.float32) #number of panels input to model
y = X_num.copy() #target/output is number of panels

#-----------------------------------------------------------------------

for n in range(10):
    x = np.random.randint(0, len(X_img) - 1)
    _, row = list(df.iterrows())[x]
    img = load_image(Path(IMAGES_PATH / row[FILENAME_COL]))
    img = np.expand_dims(img, axis=0) #add batch dimension
    pred = model.predict(img, verbose=0)[0][0]
    print(f"\npredicted number of panels: {round(float(pred))}")
    print(f"\ncorrect number of panels: {X_num[x]}")
    print(f"\nfilename: {X_img}")
    img = Image.open(Path(IMAGES_PATH / row[FILENAME_COL]))
    img.show()

