import os
import vtk

objPath = r"E:/LeeYujeong/VCLab/철도 AR/학습데이터셋 생성/Input_Data"
outputPath = r"E:/LeeYujeong/VCLab/철도 AR/학습데이터셋 생성/normalized_test"
os.makedirs(outputPath, exist_ok=True)  # 폴더가 없으면 생성, 이미 존재하면 무시

obj_files = [file for file in os.listdir(objPath) if file.endswith('.obj')]

for obj_file in obj_files:
    reader = vtk.vtkOBJReader()
    reader.SetFileName(os.path.join(objPath, obj_file))
    reader.Update()

    polydata = reader.GetOutput()

    bounds = polydata.GetBounds()
    model_size = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

    transform = vtk.vtkTransform()
    transform.Scale(1.0/model_size, 1.0/model_size, 1.0/model_size)

    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetInputData(polydata)
    transform_filter.SetTransform(transform)
    transform_filter.Update()

    normalized_polydata = transform_filter.GetOutput()
    file_name = os.path.join(outputPath, obj_file)

    writer = vtk.vtkOBJWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(normalized_polydata)
    writer.Write()
