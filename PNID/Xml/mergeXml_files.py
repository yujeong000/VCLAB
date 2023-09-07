# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 21:22:26 2023

@author: 이유정

큰 심볼 xml과 작은 심볼 xml 병합
- etc 태그는 병합에 반영하지 않는다. xml을 병합할 때 <etc/>로 추가됨
- 폴더 속 xml 전체 merge (Large폴더 + Small폴더 -> merge)

mergeXml 대비 변경사항
- 파일 1개에서 폴더에 있는 모든 파일로 변경

"""

import xml.dom.minidom
import xml.etree.ElementTree as ET
import os

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    objects_list = []
    for symbol_object in root.findall('symbol_object'):
        _type = symbol_object.find('type').text
        _class = symbol_object.find('class').text
        xmin = symbol_object.find('bndbox/xmin').text
        ymin = symbol_object.find('bndbox/ymin').text
        xmax = symbol_object.find('bndbox/xmax').text
        ymax = symbol_object.find('bndbox/ymax').text
        isLarge = symbol_object.find('isLarge').text
        degree = symbol_object.find('degree').text
        flip = symbol_object.find('flip').text
        
        objects_list.append({
            '_type': _type,
            '_class': _class,
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
            'isLarge': isLarge,
            'degree': degree,
            'flip': flip
        })
    
    return objects_list

def create_xml(objects_list, filename):
    xmlRoot = ET.Element("annotation")

    for obj in objects_list:
        elementSymbol = ET.Element("symbol_object")
        elementType = ET.Element("type")
        elementType.text = obj['_type']
        elementClass = ET.Element("class")
        elementClass.text = obj['_class']

        elementBndbox = ET.Element("bndbox")
        elementXmin = ET.Element("xmin")
        elementXmin.text = obj['xmin']
        elementYmin = ET.Element("ymin")
        elementYmin.text = obj['ymin']
        elementXmax = ET.Element("xmax")
        elementXmax.text = obj['xmax']
        elementYmax = ET.Element("ymax")
        elementYmax.text = obj['ymax']

        elementBndbox.append(elementXmin)
        elementBndbox.append(elementYmin)
        elementBndbox.append(elementXmax)
        elementBndbox.append(elementYmax)

        elementIsLarge = ET.Element("isLarge")
        elementIsLarge.text = obj['isLarge'] 

        elementDegree = ET.Element("degree")
        elementDegree.text = obj['degree']

        elementFlip = ET.Element("flip")
        elementFlip.text = obj['flip']

        elementEtc = ET.Element("etc")

        elementSymbol.append(elementType)
        elementSymbol.append(elementClass)
        elementSymbol.append(elementBndbox)
        elementSymbol.append(elementIsLarge)
        elementSymbol.append(elementDegree)
        elementSymbol.append(elementFlip)
        elementSymbol.append(elementEtc)

        xmlRoot.append(elementSymbol)

    xmlstr = xml.dom.minidom.parseString(ET.tostring(xmlRoot)).toprettyxml(indent="    ")

    output_filename = filename
    with open(output_filename, "w") as file:
        file.write(xmlstr)

    return output_filename

# 큰 심볼 XML 폴더 경로
large_xml_folder = r'F:\VCLab\PNID\xml 병합\Large'
# 작은 심볼 XML 폴더 경로
small_xml_folder = r'F:\VCLab\PNID\xml 병합\Small'
# 결과 xml을 저장할 폴더 경로
output_folder = r'0829_files_result'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# XML 폴더 내의 모든 XML 파일에 대해 처리
for xml_file in os.listdir(large_xml_folder):
    if not xml_file.endswith('.xml'):
        continue
    large_xml_file_path = os.path.join(large_xml_folder, xml_file)
    small_xml_file_path = os.path.join(small_xml_folder, xml_file)

    
    large_objects_list = parse_xml(large_xml_file_path)
    small_objects_list = parse_xml(small_xml_file_path)
    
    merged_objects_list = large_objects_list + small_objects_list
        
    merged_xml_file = os.path.join(output_folder, xml_file)
    output_filename = create_xml(merged_objects_list, merged_xml_file)
    print(output_filename)