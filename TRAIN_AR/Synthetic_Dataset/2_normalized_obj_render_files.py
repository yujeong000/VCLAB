import vtk
import os

# Icosahedron 생성
icosahedron = vtk.vtkPlatonicSolidSource()
icosahedron.SetSolidTypeToIcosahedron()
icosahedron.Update()
# Icosahedron의 PolyData 가져오기
polydata = icosahedron.GetOutput()

# vtkTransform 크기 조절
transform = vtk.vtkTransform()
transform.Scale(4.0, 4.0, 4.0)

transform_filter = vtk.vtkTransformFilter()
transform_filter.SetInputData(polydata)
transform_filter.SetTransform(transform)
transform_filter.Update()

# 크기 조정된 polydata
scaled_polydata = transform_filter.GetOutput()

# Subdivision
subdivision_filter = vtk.vtkLoopSubdivisionFilter()
subdivision_filter.SetNumberOfSubdivisions(1)
subdivision_filter.SetInputData(scaled_polydata)
subdivision_filter.Update()

# Subdivision 된 PolyData 가져오기
subdivided_polydata = subdivision_filter.GetOutput()

# 정점 개수 확인
num_vertices = subdivided_polydata.GetNumberOfPoints()
# 정점 좌표 가져오기
vertices = []
for i in range(num_vertices):
    vertex = subdivided_polydata.GetPoint(i)
    vertices.append(vertex)

# Create the 'rendering' folder if it doesn't exist
rendering_folder = "rendering_test"
if not os.path.exists(rendering_folder):
    os.mkdir(rendering_folder)

# polydata를 vtkPolyDataMapper와 vtkActor로 변환
mapper = vtk.vtkPolyDataMapper()
if vtk.VTK_MAJOR_VERSION <= 5:
    mapper.SetInput(subdivided_polydata)
else:
    mapper.SetInputData(subdivided_polydata)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a rendering window and renderer
renWin = vtk.vtkRenderWindow()
ren = vtk.vtkRenderer()
renWin.AddRenderer(ren)

# Create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# 카메라
camera = vtk.vtkCamera()
ren.SetActiveCamera(camera)

FolderName = ["BCU-ASSY-1", "BCU-ASSY-2", "BCU-ASSY-3", "BCU-ASSY-4", "BCU-ASSY-5", "BCU-BACK-PART", "ECU-ASSY-1"]

for i in range(len(FolderName)):
    folder_path = os.path.join(rendering_folder, FolderName[i])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    obj_path = os.path.join("E:/LeeYujeong/VCLab/철도 AR/학습데이터셋 생성/normalized_test", f"{FolderName[i]}.obj")
    
    reader = vtk.vtkOBJReader()
    reader.SetFileName(obj_path)
    reader.Update()
    
    ren.RemoveAllViewProps()  # 렌더러 초기화
    
    for num, vertex in enumerate(vertices):
        camera.SetPosition(vertex)
        
        # Assign actor to the renderer
        ren.AddActor(actor)
        renWin.Render()

        # 이미지 저장
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(renWin)
        window_to_image_filter.Update()

        png_writer = vtk.vtkPNGWriter()
        png_writer.SetFileName(os.path.join(folder_path, f"{FolderName[i]}_{num}.png"))
        png_writer.SetInputConnection(window_to_image_filter.GetOutputPort())
        png_writer.Write()
    
    ren.RemoveAllViewProps()
