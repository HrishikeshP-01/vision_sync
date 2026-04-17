import numpy as np
import cv2
from colorblind import colorblind
import os

def simulate_color_blindness(image_path: str, colorblind_type: str, output_folder: str):
    img_bgr = cv2.imread(image_path)
    img_rgb = img_bgr[..., ::-1]

    simulated_img_rgb = colorblind.simulate_colorblindness(img_rgb, colorblind_type=colorblind_type)
    simulated_img_bgr = simulated_img_rgb[..., ::-1]

    img_name = str(image_path).split('\\')[-1]
    print(img_name)
    folder_path = f'{output_folder}/{colorblind_type}'
    os.makedirs(folder_path, exist_ok=True)
    
    cv2.imwrite(f'{output_folder}/{colorblind_type}/{img_name}', simulated_img_bgr)


