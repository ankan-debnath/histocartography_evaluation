from utils.image_processor import Image_Processor

import pandas as pd
from tqdm import tqdm
import os

image_processor = Image_Processor()
OUTPUT_FOLDER = 'Output_Folder'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



image_dir = '/root/.cache/kagglehub/datasets/samsrithajalukuri/pathvqa-dataset/versions/1/train'

df = pd.read_csv('/root/.cache/kagglehub/datasets/samsrithajalukuri/pathvqa-dataset/versions/1/testrenamed.csv')
df = df.drop_duplicates(subset=["image"], keep="first")
df['image_path'] = image_dir + '/' + df['image'] + '.png'

for _, row in tqdm(df.iterrows(), len(df)):
    image_path = row['image_path']
    image_id = row['image']
    classification = image_processor.classify_image(image_path)
    if classification == "pathology":
        patch_folder = os.path.join(OUTPUT_FOLDER, image_id)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        image_processor.generate_patches(image_path, patch_folder)

