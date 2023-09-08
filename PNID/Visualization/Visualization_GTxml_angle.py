import cv2
import numpy as np
import xml.etree.ElementTree as ET

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    objects_list = []
    for symbol_object in root.findall('symbol_object'):
        x1 = int(symbol_object.find('bndbox/x1').text)
        y1 = int(symbol_object.find('bndbox/y1').text)
        x2 = int(symbol_object.find('bndbox/x2').text)
        y2 = int(symbol_object.find('bndbox/y2').text)
        x3 = int(symbol_object.find('bndbox/x3').text)
        y3 = int(symbol_object.find('bndbox/y3').text)
        x4 = int(symbol_object.find('bndbox/x4').text)
        y4 = int(symbol_object.find('bndbox/y4').text)
        degree = float(symbol_object.find('degree').text)
        
        objects_list.append({
            'points': np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], dtype=np.int32),
            'degree': degree
        })
    
    return objects_list


# XML 파일 경로
xml_file = r'C:/Users/VCLAB/Desktop/VCLap/PNID/xml출력코드+4-2점/검증A/XML/26071-203-M6-320-00060.xml'

# XML 파일 파싱하여 점들의 좌표 추출
objects_list = parse_xml(xml_file)

# print(points_list)
# 이미지 파일 경로
# image_file = r'C:/Users/VCLAB/Desktop/VCLap/PNID/visualization/JPG_20230228/26071-200-M6-052-00001.jpg'
# 이미지 파일 경로
image_file = r'JPG_20230228/26071-203-M6-320-00060.jpg'

# 이미지 로드
img = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
# cv2.imshow("dd", img)

# 추출한 점들의 좌표를 컨투어로 그리기
# 추출한 객체 정보를 기반으로 컨투어와 각도 표시
for obj in objects_list:
    points = obj['points']
    degree = obj['degree']
    
    # 컨투어 그리기
    cv2.drawContours(img, [points], 0, (0, 0, 255), 2)
    
    # 텍스트 표시 위치 설정
    text_position = tuple(points[0])
    
    # 각도 텍스트 추가
    text = f"{degree:.1f}"
    cv2.putText(img, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

# 결과 이미지 저장
output_file = r'right_result/result.jpg'
cv2.imwrite(output_file, img)