# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 21:55:24 2023

@author: 이유정

xml에서 degree를 휴리스틱하게 보정
- 파일->폴더로 변경

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

def adjust_angle(angle):
    angle = round(angle/15)*15
    return angle

# XML 폴더 경로
xml_folder = r'F:\VCLab\PNID\xml 병합\Merge\\'

# 결과 xml을 저장할 폴더 경로
output_folder = r'AdjustDegree'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

for xml_file in os.listdir(xml_folder):
    if not xml_file.endswith('.xml'):
        continue
    xml_file_path = os.path.join(xml_folder, xml_file)
    objects_list = parse_xml(xml_file_path)

    #각도 보정
    for obj in objects_list:
        degree = int(obj['degree'])
        degree = adjust_angle(degree)
        obj['degree'] = str(degree)
        
    result_xml_file = os.path.join(output_folder, xml_file)
    output_filename = create_xml(objects_list, result_xml_file)
    print(output_filename)