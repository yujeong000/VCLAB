import os
import cv2
import random
import json
import numpy as np

images = []
annotations = []
annotation_id = 0
def composite_images_centered(background, background_id, images_to_insert, grid_pixel_size, folder_id_list, id_folder_map):
    print("a")
    global annotation_id
    
    # 배경이미지 크기 구하기
    h, w, _ = background.shape
    # 그리드 사이즈 구하기
    num_rows = h // grid_pixel_size
    num_cols = w // grid_pixel_size

    # 기록된 그리드의 위치를 저장하는 리스트
    inserted_grids = []

    for i in range(len(images_to_insert)):
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
        
        image_to_insert = images_to_insert[i]

        if image_to_insert.shape[2] == 4:  # Check if the image has an alpha channel
            # 배경 이미지와 이미지를 비교하여 크기를 맞춤
            max_side = max(image_to_insert.shape[0], image_to_insert.shape[1])
            resized_h = int(image_to_insert.shape[0] * (grid_pixel_size / max_side))
            resized_w = int(image_to_insert.shape[1] * (grid_pixel_size / max_side))

            image_to_insert_resized = cv2.resize(image_to_insert, (resized_w, resized_h))

            # 그리드 중심점에 이미지를 합성하기 위해 위치를 조정
            y1, y2 = int(center_y - resized_h / 2), int(center_y + resized_h / 2)
            x1, x2 = int(center_x - resized_w / 2), int(center_x + resized_w / 2)

            # 합성할 이미지의 알파 채널을 추출
            alpha_channel = image_to_insert_resized[:, :, 3] / 255.0

            # 배경 이미지에 합성할 이미지를 적용 (알파 채널을 이용하여 합성)
            for c in range(3):
                background[y1:y2, x1:x2, c] = (1 - alpha_channel) * background[y1:y2, x1:x2, c] + alpha_channel * image_to_insert_resized[:, :, c] * alpha_channel

        rect = (1,1,image_to_insert.shape[0],image_to_insert.shape[1])

        # 배경 제거를 위한 마스크 생성
        mask = np.zeros(image_to_insert.shape[:2],np.uint8)
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
        
        # 알파 채널 값 가져오기
        alpha_channel = image_to_insert[:, :, 3] / 255.0
        
        # 컬러 채널 값 가져오기
        color_channels = image_to_insert[:, :, :3]
        
        # 8-bit 3채널 컬러 이미지로 변환
        image_to_insert_3ch = (color_channels * alpha_channel[:, :, np.newaxis]).astype(np.uint8)

        # GrabCut 알고리즘 수행
        cv2.grabCut(image_to_insert_3ch,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)

        # 마스크에서 전경에 해당하는 부분을 1로 설정
        mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')

        # GrabCut에서 추출된 물체 영역 좌표
        contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(contours[0])
        x = int(x*(grid_pixel_size/image_to_insert.shape[0]))
        y = int(y*(grid_pixel_size/image_to_insert.shape[1]))
        w = int(w*(grid_pixel_size/image_to_insert.shape[0]))
        h = int(h*(grid_pixel_size/image_to_insert.shape[1]))
        cv2.rectangle(background, (x1+x, y1+y), (x1 + x+w, y1 + y+h), (0, 0, 0), 7)
        cv2.putText(background, id_folder_map[folder_id_list[i]], (x1+x, y1+y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # annotations 리스트에 정보 추가
        bbox = [x1 + x, x2 + y, w, h]
        annotations.append({
            "id": annotation_id,
            "bbox": bbox,
            "image_id": background_id,
            "segmentation": [],
            "ignore": 0,
            "area": w*h,  # bbox의 너비와 높이로 area 계산 (수정 가능)
            "iscrowd": 0,
            "category_id": folder_id_list[i]
        })
        
        annotation_id += 1
    print("b")
    return background

try:

    
    # 배경 이미지 폴더 경로
    background_folder = "Background"
    
    # 배경을 제거한 이미지 폴더 경로
    remove_background_folder = "Remove_Background"
    
    # 합성된 이미지를 저장할 폴더 경로
    output_folder = "Training_Data"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    # 배경 이미지 목록
    background_images = []
    for filename in os.listdir(background_folder):
        if filename.lower().endswith(".jpg"):
            img_path = os.path.join(background_folder, filename)
            img = cv2.imread(img_path)
            background_images.append(img)
    
    # print(len(background_images))
    
    folder_id_map = {}
    folder_id_counter = 0
    folder_id_list = []
    i = 0
    # 배경 이미지 1장당 전체 출력 이미지 1개를 생성하도록 수정
    for bg_image in background_images:
        for _ in range(1):
            # 삽입될 이미지 개수를 랜덤하게 설정 (1~4장)
            num_images_to_insert = random.randint(1, 4)
        
            # 이미 등록된 하위 폴더의 id를 가져오거나 새로운 id 생성하여 딕셔너리에 저장
            for folder_name in os.listdir(remove_background_folder):
                if folder_name not in folder_id_map:
                    folder_id_map[folder_name] = folder_id_counter
                    folder_id_counter += 1
            id_folder_map = {v: k for k, v in folder_id_map.items()}
        
            # 삽입될 이미지들이 있는 하위 폴더들을 랜덤하게 선택
            selected_folders = random.sample(os.listdir(remove_background_folder), num_images_to_insert)
        
            bg_folder_images = []
            for folder_name in selected_folders:
                folder_path = os.path.join(remove_background_folder, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                folder_id_list.append(folder_id_map[folder_name])
                folder_images = [img for img in os.listdir(folder_path) if img.lower().endswith(".png")]
                if folder_images:
                    img_path = os.path.join(folder_path, random.choice(folder_images))
                    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                    bg_folder_images.append(img)
            
            random_number = random.randint(150, 400)
            print(i)
            
            composite_img = composite_images_centered(bg_image.copy(), i, bg_folder_images, random_number, folder_id_list, id_folder_map)
            composite_img_gray = cv2.cvtColor(composite_img, cv2.COLOR_BGR2GRAY)
            output_filename = f"{i}.png"
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, composite_img_gray)
            
            # 출력 이미지의 가로와 세로 크기
            output_width, output_height = composite_img.shape[1], composite_img.shape[0]
    
            # images 리스트에 합성된 이미지 정보 추가
            images.append({
                "file_name": output_filename,
                "width": output_width,
                "height": output_height,
                "id": i
            })
            
            print(i)
            i += 1
    
    data = {
        "type": "instances",
        "images": images,
        "annotations": annotations
    }
    
    # JSON 파일로 저장
    with open("Training_Data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

except Exception as e:
    print("오류가 발생했습니다:", e)