from rembg import remove
from PIL import Image
import os

# 이미지를 불러와서 배경 제거하고 저장할 폴더
input_folder = "rendering"  # 이미지 폴더
output_folder = "Remove_Background"  # 배경 제거된 이미지를 저장할 폴더

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# 이미지 폴더 내의 모든 하위 폴더와 이미지 파일에 대해 배경 제거
for folder_name in os.listdir(input_folder):
    folder_path = os.path.join(input_folder, folder_name)
    if not os.path.isdir(folder_path):
        continue  # 폴더가 아닌 경우 건너뜁니다.

    output_subfolder = os.path.join(output_folder, folder_name)
    if not os.path.exists(output_subfolder):
        os.mkdir(output_subfolder)

    # 이미지 폴더의 하위 폴더 내의 모든 이미지 파일에 대해 배경 제거
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):  # 확장자가 .png인 이미지만 처리
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_subfolder, f"{os.path.splitext(filename)[0]}_rembg.png")

            input_img = Image.open(input_path)  # 이미지 로드
            output_img = remove(input_img)  # 배경 제거

            output_img.save(output_path)  # 배경 제거된 이미지 저장
