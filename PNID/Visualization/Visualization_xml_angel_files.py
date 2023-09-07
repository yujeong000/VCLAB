# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 18:01:31 2023

@author: 이유정

xml을 파싱하여 각도와 좌표번호를 출력하는 코드

TODO
- 좌표 회전하여 그리기
"""

import cv2
import numpy as np
import xml.etree.ElementTree as ET
import os
import math

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    objects_list = []
    for symbol_object in root.findall('symbol_object'):
        x1 = int(symbol_object.find('bndbox/xmin').text)
        y1 = int(symbol_object.find('bndbox/ymin').text)
        x3 = int(symbol_object.find('bndbox/xmax').text)
        y3 = int(symbol_object.find('bndbox/ymax').text)
        degree = float(symbol_object.find('degree').text)
        
        objects_list.append({
            'points': np.array([[x1, y1], [x3, y1], [x3, y3], [x1, y3]], dtype=np.int32),
            'degree': degree
        })
    
    return objects_list

def rotate_bbox(obj):
    def rotate(point, degree):
        radian = degree * (float)(math.pi / 180);
        x = math.cos(radian) * point[0] - math.sin(radian) * point[1];
        y = math.sin(radian) * point[0] + math.cos(radian) * point[1];
        return [int(x), int(y)]
        
    points = obj['points']
    degree = obj['degree']
    # print(degree)
    
    point1 = [points[0][0], points[0][1]]
    point2 = [points[1][0], points[1][1]]
    point3 = [points[2][0], points[2][1]]
    point4 = [points[3][0], points[3][1]]
    
    center_x = (point1[0] + point3[0]) // 2
    center_y = (point1[1] + point3[1]) // 2
    
    point1 = [point1[0]-center_x, point1[1]-center_y]
    point2 = [point2[0]-center_x, point2[1]-center_y]
    point3 = [point3[0]-center_x, point3[1]-center_y]
    point4 = [point4[0]-center_x, point4[1]-center_y]
    
    point1 = rotate(point1, degree)
    point2 = rotate(point2, degree)
    point3 = rotate(point3, degree)
    point4 = rotate(point4, degree)
    
    point1 = [point1[0]+center_x, point1[1]+center_y]
    point2 = [point2[0]+center_x, point2[1]+center_y]
    point3 = [point3[0]+center_x, point3[1]+center_y]
    point4 = [point4[0]+center_x, point4[1]+center_y]
    
    return point1, point2, point3, point4
    

# XML 폴더 경로
xml_folder = r'../Xml/Txt2Xml_files_result'

# 이미지 폴더 경로
image_folder = r'JPG_20230228'

# 결과 이미지를 저장할 폴더 경로
output_folder = r'Visualization_Txt2Xml_files_result'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)


# XML 폴더 내의 모든 XML 파일에 대해 처리
for xml_file in os.listdir(xml_folder):
    if not xml_file.endswith('.xml'):
        continue
    
    xml_file_path = os.path.join(xml_folder, xml_file)
    
    # XML 파일 파싱하여 점들의 좌표 추출
    objects_list = parse_xml(xml_file_path)
    
    # XML 파일에 대응하는 이미지 파일 찾기
    image_file = os.path.join(image_folder, xml_file.replace('.xml', '.jpg'))
    
    if not os.path.isfile(image_file):
        print(f"경고: {image_file}에 대응하는 이미지 파일이 없습니다.")
        continue
    
    # 이미지 로드
    img = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
    
    # 추출한 점들의 좌표를 컨투어로 그리고, 각도 텍스트 추가
    for obj in objects_list:
        points = obj['points']
        degree = obj['degree']

        # 컨투어 그리기
        point1, point2, point3, point4 = rotate_bbox(obj)
        # point1 = [int(points[0][0]), int(points[0][1])]
        # point2 = [int(points[1][0]), int(points[1][1])]
        # point3 = [int(points[2][0]), int(points[2][1])]
        # point4 = [int(points[3][0]), int(points[3][1])]
        
        box = [point1, point2, point3, point4]
        box = np.array(box)
        
        cv2.drawContours(img, [box], 0, (0, 255, 0), 4)
        # cv2.circle(img, tuple(point1), 5, (0, 255, 0), -1)
        cv2.putText(img, "1", point1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "2", point2, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "3", point3, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, "4", point4, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 텍스트 표시 위치 설정
        text_position = tuple(point1)
        
        # 각도 텍스트 추가
        text = f"{degree:.1f}"
        cv2.putText(img, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # 결과 이미지 저장
    output_file = os.path.join(output_folder, xml_file.replace('.xml', '.jpg'))
    cv2.imwrite(output_file, img)
    print(output_file)
