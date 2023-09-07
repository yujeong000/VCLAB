import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from tqdm import tqdm  # tqdm 라이브러리 추가

# JSON 파일 경로
json_file_path = r"E:/LeeYujeong/VCLAB/Desktop/VCLab/철도 AR/학습데이터셋 생성/visualizaion/230807_Data2/Training_Data.json"
image_directory = r"E:/LeeYujeong/VCLAB/Desktop/VCLab/철도 AR/학습데이터셋 생성/visualizaion/230807_Data2/Training_Data"
output_directory = r"E:/LeeYujeong/VCLAB/Desktop/VCLab/철도 AR/학습데이터셋 생성/visualizaion/230807_Data2/visualization"

# JSON 파일 불러오기
with open(json_file_path, "r") as json_file:
    dataset = json.load(json_file)

# 이미지 및 객체 정보 추출
images = dataset["images"]
annotations = dataset["annotations"]
categories = dataset["categories"]

# 폴더가 없으면 생성
os.makedirs(output_directory, exist_ok=True)

# 이미지와 객체 정보를 가지고 시각화 및 저장
for image_info in tqdm(images, desc="Processing Images"):  # tqdm 사용
    image_id = image_info["id"]
    image_path = os.path.join(image_directory, image_info['file_name'])
    image = Image.open(image_path)

    # 이미지 출력
    plt.figure(figsize=(8, 8))
    plt.imshow(image)

    # 해당 이미지에 대한 객체 정보 추출
    objects = [anno for anno in annotations if anno["image_id"] == image_id]

    for obj in objects:
        bbox = obj["bbox"]
        category_id = obj["category_id"]
        category_name = next(cat["name"] for cat in categories if cat["id"] == category_id)

        # 경계 상자 시각화
        rect = patches.Rectangle(
            (bbox[0], bbox[1]), bbox[2], bbox[3],
            linewidth=1, edgecolor='r', facecolor='none'
        )
        plt.gca().add_patch(rect)
        plt.text(bbox[0], bbox[1], category_name, color='r', verticalalignment='top')

    plt.axis('off')
    
    # 이미지 저장
    output_path = os.path.join(output_directory, image_info['file_name'])
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

print("이미지 저장이 완료되었습니다.")
