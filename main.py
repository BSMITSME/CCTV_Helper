import torch
from roboflow import Roboflow
import yaml
from ultralytics import YOLO
def getData() :
    rf = Roboflow(api_key="SGagU7TQB5MnkpS0AJus")
    project = rf.workspace("cctv-zl5y7").project("help-sign-detector-hphj8")
    dataset = project.version(2).download("yolov8")


def setData() :
    data= {
        'train': '/Users/seonminbaek/PycharmProjects/modelTraining/Help-Sign-Detector-2/train/images/',
        'val': '/Users/seonminbaek/PycharmProjects/modelTraining/Help-Sign-Detector-2/valid/images/',
        'test': '/Users/seonminbaek/PycharmProjects/modelTraining/Help-Sign-Detector-2/test/images/',
        'names': ['face', 'help'],
        'nc': 2
    }

    with open('Help-Sign-Detector-2/CCTV_HandSign.yaml', 'w') as f:
        yaml.dump(data, f)
    with open('Help-Sign-Detector-2/CCTV_HandSign.yaml', 'r') as f:
        CCTV_HandSign_yaml = yaml.safe_load(f)
        print(CCTV_HandSign_yaml)

import platform
if __name__ == '__main__' :
    getData()
    setData()
    model = YOLO('yolov8n.pt')
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

    print(f"PyTorch version:{torch.__version__}")  # 1.12.1 이상
    print(f"MPS 장치를 지원하도록 build 되었는지: {torch.backends.mps.is_built()}")  # True 여야 합니다.
    print(f"MPS 장치가 사용 가능한지: {torch.backends.mps.is_available()}")  # True 여야 합니다.
    print(platform.platform())

    print(device)
    model.train(data='Help-Sign-Detector-2/CCTV_HandSign.yaml', epochs=1500, patience=500, batch=32, imgsz=640, device = 'mps')

    # model에 적용된 label 확인
    print(type(model.names), len(model.names))
    print(model.names)

    result = model.predict(source='Help-Sign-Detector-2/test/images/', save=True)