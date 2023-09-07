import os
import cv2
import random
import json
import numpy as np
"""
background_images : cv2.imread로 읽은 배경이미지들이 담겨있음
background_image : 이미지 1장
composite_images_list: 합성할 이미지들이 담겨있음
"""
def create_folder_id_maps(remove_background_folder):
    folder_id_map = {}
    folder_id_counter = 0

    for folder_name in os.listdir(remove_background_folder):
        if folder_name not in folder_id_map:
            folder_id_map[folder_name] = folder_id_counter
            folder_id_counter += 1

    id_folder_map = {v: k for k, v in folder_id_map.items()}
    return folder_id_map, id_folder_map


def load_composite_images(selected_folders, remove_background_folder):
    composite_images_list = []

    for folder_name in selected_folders:
        folder_path = os.path.join(remove_background_folder, folder_name)
        folder_images = [img for img in os.listdir(folder_path) if img.lower().endswith(".png")]
        img_path = os.path.join(folder_path, random.choice(folder_images))
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        composite_images_list.append(img)
    
    return composite_images_list

def load_composite_images_even(selected_folders, remove_background_folder):
    composite_images_list = []

    for folder_name in selected_folders:
        folder_path = os.path.join(remove_background_folder, folder_name)
        folder_images = [img for img in os.listdir(folder_path) if img.lower().endswith(".png")]

        # Select only even-indexed images
        even_images = [img for idx, img in enumerate(folder_images) if idx % 2 == 0]

        if even_images:  # Make sure there are even images in the folder
            img_name = random.choice(even_images)
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            composite_images_list.append(img)
    
    return composite_images_list

def load_composite_images_odd(selected_folders, remove_background_folder):
    composite_images_list = []

    for folder_name in selected_folders:
        folder_path = os.path.join(remove_background_folder, folder_name)
        folder_images = [img for img in os.listdir(folder_path) if img.lower().endswith(".png")]

        # Select only odd-indexed images
        odd_images = [img for idx, img in enumerate(folder_images) if idx % 2 != 0]

        if odd_images:  # Make sure there are odd images in the folder
            img_name = random.choice(odd_images)
            img_path = os.path.join(folder_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            composite_images_list.append(img)
    
    return composite_images_list

def grabcut_mask_contours(composite_image):
    rect = (1,1,composite_image.shape[0],composite_image.shape[1])
    # 배경 제거를 위한 마스크 생성
    mask = np.zeros(composite_image.shape[:2],np.uint8)
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)   
    # 알파 채널 값 가져오기
    alpha_channel = composite_image[:, :, 3] / 255.0
    # 컬러 채널 값 가져오기
    color_channels = composite_image[:, :, :3]
    # 8-bit 3채널 컬러 이미지로 변환
    composite_image_3ch = (color_channels * alpha_channel[:, :, np.newaxis]).astype(np.uint8)
    # GrabCut 알고리즘 수행
    cv2.grabCut(composite_image_3ch,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    # 마스크에서 전경에 해당하는 부분을 1로 설정
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    # GrabCut에서 추출된 물체 영역 좌표
    contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours

def create_annotations(bbox, background_id, w, h, selected_folders):
    global annotation_id
    annotations.append({
        "id": annotation_id,
        "bbox": bbox,
        "image_id": background_id,
        "segmentation": [],
        "ignore": 0,
        "area": w*h,  # bbox의 너비와 높이로 area 계산 (수정 가능)
        "iscrowd": 0,
        "category_id": folder_id_map[selected_folders]
    })
    annotation_id+=1

def composite_images_centered(background, composite_images_list, selected_folders, output_filename_count):
    # 배경이미지 크기 구하기
    h, w, _ = background.shape
    
    # 그리드 사이즈 구하기
    grid_pixel_size = random.randint(150, 400)
    num_rows = h // grid_pixel_size
    num_cols = w // grid_pixel_size
    
    # 합성된 그리드의 위치를 저장하는 리스트
    inserted_grids = []
    
    for i in range(len(composite_images_list)):
        while True:
            # 합성될 셀 선택
            row = random.randint(0, num_rows - 1)
            col = random.randint(0, num_cols - 1)
            
            # 이미 합성된 그리드가 아닌 경우에만 합성 진행
            if (row, col) not in inserted_grids:
                break
        # 합성된 셀 리스트에 추가
        inserted_grids.append((row, col))
        
        # 그리드 중심점 계산
        center_y, center_x = (row + 0.5) * grid_pixel_size, (col + 0.5) * grid_pixel_size
        
        composite_image = composite_images_list[i]
        
        if composite_image.shape[2] == 4:  # Check if the image has an alpha channel
            # 배경 이미지와 이미지를 비교하여 크기를 맞춤
            max_side = max(composite_image.shape[0], composite_image.shape[1])
            resized_h = int(composite_image.shape[0] * (grid_pixel_size / max_side))
            resized_w = int(composite_image.shape[1] * (grid_pixel_size / max_side))

            composite_image_resized = cv2.resize(composite_image, (resized_w, resized_h))

            # 그리드 중심점에 이미지를 합성하기 위해 위치를 조정
            y1, y2 = int(center_y - resized_h / 2), int(center_y + resized_h / 2)
            x1, x2 = int(center_x - resized_w / 2), int(center_x + resized_w / 2)

            # 합성할 이미지의 알파 채널을 추출
            alpha_channel = composite_image_resized[:, :, 3] / 255.0

            # 배경 이미지에 합성할 이미지를 적용 (알파 채널을 이용하여 합성)
            for c in range(3):
                background[y1:y2, x1:x2, c] = (1 - alpha_channel) * background[y1:y2, x1:x2, c] + alpha_channel * composite_image_resized[:, :, c] * alpha_channel
            
        contours = grabcut_mask_contours(composite_image)
        # print(contours)
        x, y, w, h = cv2.boundingRect(contours[0])
        x = int(x*(grid_pixel_size/composite_image.shape[0]))
        y = int(y*(grid_pixel_size/composite_image.shape[1]))
        w = int(w*(grid_pixel_size/composite_image.shape[0]))
        h = int(h*(grid_pixel_size/composite_image.shape[1]))
        bbox = [x1 + x, y1 + y, w, h]
        # print(grid_pixel_size)
        # print(composite_image.shape[0])
        # print(composite_image.shape[1])
        # print(bbox)
        # print([x1+x, y1+y, x1 + x+w, y1 + y+h])
        create_annotations(bbox, output_filename_count, w, h, selected_folders[i])
        # print([x1+x, y1+y, x1 + x+w, y1 + y+h])
        # cv2.rectangle(background, (x1+x, y1+y), (x1 + x+w, y1 + y+h), (0, 0, 0), 7)
        # cv2.putText(background, selected_folders[i], (x1+x, y1+y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    return background_gray

images = []
annotations = []
categories = []
annotation_id = 0

# 배경 이미지 폴더 경로
background_folder = "Background"

# 배경을 제거한 이미지 폴더 경로
remove_background_folder = "Remove_Background"

# 합성된 이미지를 저장할 폴더 경로
output_folder = "Test_Data_odd"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
output_filename_count = 0
# 배경 이미지 리스트
background_images = []
for filename in os.listdir(background_folder):
    img_path = os.path.join(background_folder, filename)
    img = cv2.imread(img_path)
    background_images.append(img)
        
    
for background_image in background_images:
    for _ in range(2):
        print("===")
        # 삽입될 이미지 개수를 랜덤하게 설정 (1~4장)
        num_images_to_insert = random.randint(1, 4)
        # 맵 생성
        folder_id_map, id_folder_map = create_folder_id_maps(remove_background_folder)
        
        # 삽입될 이미지들이 있는 하위 폴더들을 랜덤하게 선택
        selected_folders = random.sample(os.listdir(remove_background_folder), num_images_to_insert)
        
        composite_images_list = load_composite_images_odd(selected_folders, remove_background_folder)
        # print(len(composite_images_list))
        
        composited_img = composite_images_centered(background_image.copy(), composite_images_list, selected_folders, output_filename_count)
        
        output_filename = f"{output_filename_count}.png"
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, composited_img)
        
        
        images.append({
            "file_name": output_filename,
            "width": composited_img.shape[1],
            "height": composited_img.shape[0],
            "id": output_filename_count
        })
        
        output_filename_count += 1

# print(id_folder_map)
for i, folder_name in id_folder_map.items():
    categories.append({
        "id": i,
        "name": folder_name,
    })

data = {
    "type": "instances",
    "images": images,
    "annotations": annotations,
    "categories" : categories
}

# JSON 파일로 저장
with open("Test_Data_odd.json", "w") as json_file:
    json.dump(data, json_file, indent=4)
