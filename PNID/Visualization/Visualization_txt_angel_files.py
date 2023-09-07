# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 15:45:16 2023

@author: 이유정

txt를 파싱하여 각도와 좌표번호를 출력하는 코드
- 4점 + 각도 + class가 들어있는 txt파일


"""

import numpy as np
import math
import os
import cv2

def read_four_point_txt(file_path):
    fourPointTxt = open(file_path, "r")
    contents = fourPointTxt.read()
    contentsList = contents.split('\n')
    
    def filter_empty(item):
        return item != ['']
    
    fourPoint = list(filter(filter_empty, [tmp.split(' ') for tmp in contentsList]))
    return fourPoint


def convert_points(fourPoint):
    def remove_text(sublist):
        return sublist[:-2]

    def convert_sublist(sublist):
        return [(float(sublist[i]), float(sublist[i+1])) for i in range(0, len(sublist), 2)]

    converted_points = []
    for sublist in fourPoint:
        sublist = remove_text(sublist)
        sublist = convert_sublist(sublist)
        converted_points.append(sublist)

    return converted_points

def extract_rectangle_properties(pts):
    def calculate_distance(x1, y1, x2, y2):
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance
    
    width = calculate_distance(pts[0][0], pts[0][1], pts[1][0], pts[1][1]) 
    height = calculate_distance(pts[1][0], pts[1][1], pts[2][0], pts[2][1])
    center_x = (pts[0][0] + pts[2][0]) / 2
    center_y = (pts[0][1] + pts[2][1]) / 2
    return width, height, center_x, center_y


def rbox2hbox(center_x, center_y, width, height):
    before_left_top_point = [int(center_x - (width / 2)), int(center_y - (height / 2))]
    before_right_top_point = [int(center_x + (width / 2)), int(center_y - (height / 2))]
    before_left_bottom_point = [int(center_x - (width / 2)), int(center_y + (height / 2))]
    before_right_bottom_point = [int(center_x + (width / 2)), int(center_y + (height / 2))]
    return before_left_top_point, before_right_top_point, before_right_bottom_point, before_left_bottom_point



#4점 텍스트 파일이 들어있는 폴더 선택
txt_folder = r'F:\VCLab\PNID\xml출력코드+4-2점\0831_txt_angle_annfiles'
# 이미지 폴더 경로
image_folder = r'F:\VCLab\PNID/visualization/JPG_20230228'
# 결과를 저장할 폴더 경로
output_folder = r'0831_txt_angle_result'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# 폴더 내의 모든 txt 파일에 대해 처리
for txt_file in os.listdir(txt_folder):
    if not txt_file.endswith('.txt'):
        continue
    txt_file_path = os.path.join(txt_folder, txt_file)
    
    image_file = os.path.join(image_folder, txt_file.replace('.txt', '.jpg'))
    if not os.path.isfile(image_file):
        print(f"경고: {image_file}에 대응하는 이미지 파일이 없습니다.")
        continue
    img = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
    
    fourPoint = read_four_point_txt(txt_file_path)
    # print(fourPoint)
    #4점 텍스트 파일에서 클래스 지우고, str -> float으로 변경
    converted_points = convert_points(fourPoint)

    converted_points = np.array(converted_points, dtype=np.int32)
    
    for i in range(len(converted_points)):
        pts = converted_points[i]
        cv2.drawContours(img, [pts], 0, (0, 255, 0), 4)
        
        cv2.putText(img, "1", pts[0], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "2", pts[1], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "3", pts[2], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "4", pts[3], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 텍스트 표시 위치 설정
        text_position = tuple(pts[0])
        # print(type(float(fourPoint[i][8])))
        # 각도 텍스트 추가
        degree = np.degrees(float(fourPoint[i][8]))
        degree = int(degree)
        cv2.putText(img, str(degree), text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # 결과 이미지 저장
    output_file = os.path.join(output_folder, txt_file.replace('.txt', '.jpg'))
    cv2.imwrite(output_file, img)
    print(f"이미지 '{output_file}'가 성공적으로 저장되었습니다.")
    