import cv2
import os
import numpy as np

# 이미지를 불러와서 배경 제거하고 사각형을 그릴 폴더
input_folder = "rendering"  # 이미지 폴더
output_folder = "Remove_Background_GrabCut_Rectangle"  # 배경 제거 및 사각형 그린 이미지를 저장할 폴더

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# 이미지 폴더 내의 모든 하위 폴더와 이미지 파일에 대해 배경 제거 및 사각형 그리기
for folder_name in os.listdir(input_folder):
    folder_path = os.path.join(input_folder, folder_name)
    if not os.path.isdir(folder_path):
        continue  # 폴더가 아닌 경우 건너뜁니다.

    output_subfolder = os.path.join(output_folder, folder_name)
    if not os.path.exists(output_subfolder):
        os.mkdir(output_subfolder)

    # 이미지 폴더의 하위 폴더 내의 모든 이미지 파일에 대해 배경 제거 및 사각형 그리기
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):  # 확장자가 .png인 이미지만 처리
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_subfolder, f"{os.path.splitext(filename)[0]}_bg_removed_rect.png")

            input_img = cv2.imread(input_path)  # 이미지 로드
            rect = (1,1,input_img.shape[0],input_img.shape[1])
            
            
            # 배경 제거를 위한 마스크 생성
            mask = np.zeros(input_img.shape[:2],np.uint8)
            bgdModel = np.zeros((1,65),np.float64)
            fgdModel = np.zeros((1,65),np.float64)

            # GrabCut 알고리즘 수행
            cv2.grabCut(input_img,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)

            # 마스크에서 전경에 해당하는 부분을 1로 설정
            mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')

            # 이미지에 마스크 적용하여 배경 제거
            output_img = input_img*mask2[:,:,np.newaxis]

            # GrabCut에서 추출된 물체 영역 좌표
            contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imwrite(output_path, output_img)  # 배경 제거 및 사각형 그린 이미지 저장
