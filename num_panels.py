#packages
import pandas as pd
from pathlib import Path
import tensorflow
from tensorflow.keras.layers import Input, Conv2D, Flatten, Dense, concatenate
from tensorflow.keras.models import Model
import tensorflow as tf
#set data directory
images_path = Path('/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/VEA study - tasks for students/SOCKS project/CH Corpus/Originals')
data_path = '/Users/darbylane/Library/CloudStorage/OneDrive-UniversityofVermont/VEA study - tasks for students/SOCKS project/CH Corpus/CHB_corpus_master.xlsx' #finish path to excel spreadsheet

#extract num_panels from data_path
num_panels = pd.read_excel(data_path, usecols=["Panel #"])

#print(num_panels[1])

model_inputs = []
embeddings = []

for comic_num in range(len(list(images_path.iterdir()))):
    #use CNN for embedding
    #from Gemini
    # 1. Image Branch
    #img_input = Input(shape=(224, 224, 3), name='image_input')
    img_input = images_path[comic_num]
    # Use a pre-trained base or build basic layers
    x = Conv2D(32, (3, 3), activation='relu')(img_input)
    x = Flatten()(x)
    img_features = Dense(512, activation='relu')(x)

    # 2. Number Branch
    #num_input = Input(shape=(1,), name='number_input')
    num_input = list(num_panels.columns.values)[comic_num]
    num_features = Dense(16, activation='relu')(num_input)

    # 3. Concatenate
    combined = concatenate([img_features, num_features])

    # 4. Final Embedding Layer
    embedding = Dense(256, activation='relu', name='combined_embedding')(combined)

    model_inputs.append([img_input, num_input])
    embeddings.append(embedding)

# Build Model
embedding_model = Model(inputs=model_inputs, outputs=embeddings)

#what backbone for output?
#transformer, should be built into keras
model = Model(inputs=embeddings, ) #add outputs arg and name="transformer"

#MSE for optimization


