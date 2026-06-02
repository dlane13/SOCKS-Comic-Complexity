# ADAPT TO ORIGINAL

import pandas as pd
import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Conv2D, MaxPooling2D, Flatten, Dense,
    concatenate, Dropout, GlobalAveragePooling2D
)
from tensorflow.keras.models import Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split

# ── Config ────────────────────────────────────────────────────────────────────
IMAGES_PATH = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
                   'VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
DATA_PATH   = ('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/'
               'VEA study - tasks for students/SOCKS project/CH Corpus/CHB_corpus_master.xlsx')

IMG_SIZE    = (224, 224)
BATCH_SIZE  = 16
EPOCHS      = 50

# ── 1. Load labels ────────────────────────────────────────────────────────────
df = pd.read_excel(DATA_PATH)

# Adjust these column names to match your spreadsheet exactly
FILENAME_COL  = "Filename"   # column holding image filenames
PANEL_COL     = "Panel #"    # column holding panel counts

df = df[[FILENAME_COL, PANEL_COL]].dropna()
df[PANEL_COL] = df[PANEL_COL].astype(int)

# ── 2. Build dataset arrays ───────────────────────────────────────────────────
def load_image(filepath: Path) -> np.ndarray:
    """Load and normalise a single image to float32 in [0, 1]."""
    img = load_img(filepath, target_size=IMG_SIZE)
    arr = img_to_array(img) / 255.0
    return arr

images     = []
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

X_img    = np.array(images,     dtype=np.float32)          # (N, 224, 224, 3)
X_num    = np.array(panel_nums, dtype=np.float32)          # (N,)  — used as label
y        = X_num.copy()                                    # regression target

# ── 3. Train / validation split ───────────────────────────────────────────────
(X_img_train, X_img_val,
 y_train,     y_val) = train_test_split(X_img, y, test_size=0.2, random_state=42)

# ── 4. Model ──────────────────────────────────────────────────────────────────
# Image branch — MobileNetV2 pretrained backbone (much better than raw Conv2D)
base_model = MobileNetV2(input_shape=(*IMG_SIZE, 3),
                         include_top=False,
                         weights='imagenet')
base_model.trainable = False          # freeze during initial training

img_input    = Input(shape=(*IMG_SIZE, 3), name='image_input')
x            = base_model(img_input, training=False)
x            = GlobalAveragePooling2D()(x)
img_features = Dense(256, activation='relu')(x)
img_features = Dropout(0.3)(img_features)

# Output — single neuron, linear activation for regression
output = Dense(1, activation='linear', name='panel_count')(img_features)

model = Model(inputs=img_input, outputs=output, name='panel_counter')
model.summary()

# ── 5. Compile ────────────────────────────────────────────────────────────────
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='mse',
    metrics=['mae']          # mean absolute error ≈ average panels off
)

# ── 6. Train (frozen backbone) ────────────────────────────────────────────────
callbacks = [
    EarlyStopping(patience=8, restore_best_weights=True, monitor='val_mae'),
    ModelCheckpoint('panel_counter_best.keras', save_best_only=True, monitor='val_mae')
]

history = model.fit(
    X_img_train, y_train,
    validation_data=(X_img_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks
)

# ── 7. Fine-tune (unfreeze backbone) ─────────────────────────────────────────
print("\nFine-tuning backbone...")
base_model.trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),   # much lower LR
    loss='mse',
    metrics=['mae']
)

history_ft = model.fit(
    X_img_train, y_train,
    validation_data=(X_img_val, y_val),
    epochs=30,
    batch_size=BATCH_SIZE,
    callbacks=callbacks
)

# ── 8. Evaluate & predict ─────────────────────────────────────────────────────
loss, mae = model.evaluate(X_img_val, y_val, verbose=0)
print(f"\nValidation MAE: {mae:.2f} panels")

# Predict on a single image
def predict_panels(image_path: str) -> int:
    img = load_image(Path(image_path))
    img = np.expand_dims(img, axis=0)          # add batch dimension
    pred = model.predict(img, verbose=0)[0][0]
    return max(1, round(float(pred)))          # always at least 1 panel

# model.save('panel_counter_final.keras')