#!/usr/bin/env python3

import argparse
import cv2
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


def process_image(image_path, model_path):
    plate_cascade = cv2.CascadeClassifier(model_path)
    if plate_cascade.empty():
        return f"Error loading Haar Cascade classifier from {model_path}"
    image = cv2.imread(image_path)
    if image is None:
        return f"Could not read image: {image_path}"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25))
    if len(plates) != 0:
        for (x, y, w, h) in plates:
            roi = image[y:y+h, x:x+w]
            roi_blurred = cv2.GaussianBlur(roi, (51, 51), 0)
            image[y:y+h, x:x+w] = roi_blurred
        cv2.imwrite(image_path, image)
    return None


def main():
    parser = argparse.ArgumentParser(description="Blur license plates in BMP images using Haar Cascades")
    parser.add_argument("--directory", type=str, required=True, help="Directory containing the BMP images")
    parser.add_argument("--model", type=str, required=True,
                        help="Path to the Haar Cascade XML file for license plate detection")
    parser.add_argument("--workers", type=int, default=10, help="Number of workers for parallel processing (default is 10)")
    args = parser.parse_args()
    image_files = [os.path.join(args.directory, f)
                   for f in os.listdir(args.directory)
                   if f.lower().endswith(".bmp")]
    if not image_files:
        print("No BMP images found in the specified directory.")
        return
    image_files.sort()
    desc = "Blurring"
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_image, path, args.model): path for path in image_files}
        pbar = tqdm(total=len(image_files), desc=f"{desc:<35}", ncols=90, bar_format="{desc}{bar}| {percentage:3.0f}%")
        for _ in as_completed(futures):
            pbar.update(1)


if __name__ == "__main__":
    main()
