import os
from PIL import Image, ImageOps

def resize_images_in_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']

    for filename in os.listdir(input_folder):
        name, ext = os.path.splitext(filename)
        if ext.lower() in valid_extensions:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)  # même nom

            try:
                with Image.open(input_path) as img:
                    square_img = ImageOps.pad(img, (1080, 1080), color=(0, 0, 0))
                    square_img.save(output_path)
                    print(f"✅ {filename} redimensionnée.")
            except Exception as e:
                print(f"❌ Erreur avec {filename} : {e}")

# Dossiers
input_folder = r"C:\Users\HP\Downloads\CODES\images"
output_folder = os.path.join(input_folder, "images_1080x1080")

resize_images_in_folder(input_folder, output_folder)
