#imports
from pathlib import Path
import pandas as pd
import numpy as np

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split

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

#---------------------------------------------------------------------------

#training and validation splits
(X_img_train, X_img_val, y_train, y_val) = train_test_split(X_img, y, test_size=0.2, random_state=42) #split into training/validation/testing groups, random_state is for reproducibility

#----------------------------------------------------------------------------

#Model setup: MobileNetV2 pretrained backbone to process image
base_model = MobileNetV2(input_shape=(*IMG_SIZE, 3),
                         include_top=False,
                         weights='imagenet') #pass in pretrained weights
base_model.trainable = False #freezes during initial training

#extra layers after base model
img_input = Input(shape=(*IMG_SIZE, 3), name='image_input')
x = base_model(img_input, training=False) 
x = GlobalAveragePooling2D()(x)
img_features = Dense(256, activation='relu')(x)
#drop 30% of nodes to prevent overfitting to certain pathways
img_features = Dropout(0.3)(img_features)

# output: single neuron, linear activation function to perform regression
output = Dense(1, activation='linear', name='panel_count')(img_features)

model = Model(inputs=img_input, outputs=output, name='panel_counter')
model.summary()

#--------------------------------------------------------------------------

#compile model
model.compile(
    optimizer=Adam(learning_rate=1e-3), #low rearning rate initially
    loss='mse',
    metrics=['mae'] # mean average error is like the average number of panels off that the model is in prediction
)

#--------------------------------------------------------------------------

#now that we have the model architecture and optimization backbone, we can train!
callbacks = [
    EarlyStopping(patience=8, restore_best_weights=True, monitor='val_mae'), #if model doesn't improve after 8 epochs, stop early. "improvement" will be based on the mae of the validation set.
    ModelCheckpoint('panel_counter_best.keras', save_best_only=True, monitor='val_mae')
]

history = model.fit(
    X_img_train, y_train,
    validation_data=(X_img_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks
)

#---------------------------------------------------------------------------

#fine-tune mobilenetv2 backbone by unfreezing previously frozen weights
print("\nFine-tuning backbone...")
base_model.trainable = True

#re-compile model with newly unfrozen weights and smaller initial learning rate
model.compile(
    optimizer=Adam(learning_rate=1e-5),
    loss='mse',
    metrics=['mae']
)

history_ft = model.fit(
    X_img_train, y_train,
    validation_data=(X_img_val, y_val),
    epochs=30, #fewer epochs for fine-tuning
    batch_size=BATCH_SIZE,
    callbacks=callbacks
)

#--------------------------------------------------------------------------

#evaluate performance of model and perform testing
loss, mae = model.evaluate(X_img_val, y_val, verbose=0) #verbose=0 means no additional info
print(f"\nValidation MAE: {mae:.2f} panels")

#predict on a single image
def predict_panels(image_path: str) -> int:
    img = load_image(Path(image_path))
    img = np.expand_dims(img, axis=0) #add batch dimension
    pred = model.predict(img, verbose=0)[0][0]
    return round(float(pred))

predict_panels()
