import datetime
import time
from PIL import Image
from io import BytesIO
import os
import cv2
from ultralytics import YOLO
from kafka import KafkaProducer
from json import dumps

# Define KafkaProducer
producer = KafkaProducer(acks=0, compression_type='gzip',bootstrap_servers=['localhost:9092'])

CONFIDENCE_THRESHOLD = 0.5 #정확도 임계점
GREEN = (0, 255, 0) # 초록색 표
WHITE = (255, 255, 255) # 흰색 표시

model = YOLO('yolo_best.pt') # cqolab으로 학습된 YOLO 모델

cap = cv2.VideoCapture('/Users/seonminbaek/PycharmProjects/CCTV_HELPER/producer-cctv/istockphoto-1412822046-640_adpp_is.mp4') # 웹캠 이용
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # 창 너비
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 창 높이

# 모델에 저장된 라벨 이름 가져오기
class_list = []
dic_names = model.names
for k,v in dic_names.items() :
    class_list.append(v)
print(class_list)
i, a = 0, 0
while True:
    start = datetime.datetime.now() #fps를 계산하기 위한 동작 시간 저장

    ret, frame = cap.read() # 읽기

    # 야간 모드를 가정하기 위한 grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not ret: # ret은 True or False
        print('Cam Error')
        break

    # 웹캠 frame에서 탐지한 객체를 detection에 저장
    detection = model.predict(source=[frame], save=False)[0]
    results = []

    for data in detection.boxes.data.tolist(): # data : [xmin, ymin, xmax, ymax, confidence_score, class_id]
        confidence = float(data[4])
        
        # 임계점 0.5 이하일시 표시  안함
        if confidence < CONFIDENCE_THRESHOLD:
            continue


        # help 사인일 시 이미지 처리 (얼굴과 사인 모두 한 프레임에 나와야 함)
        if class_list[int(data[5])] == 'help' :
            #time.sleep(1000) 전체가 멈춰버림
            i+=1 #이미지 번호를 늘려주어 구별
            if i==10 : # i가 7가 되었을 때 캡쳐
                img = cv2.imwrite('Sector1_help{}.jpg'.format(a), frame)
                #이미지 읽기
                image = cv2.imread('Sector1_help{}.jpg'.format(a))
                ret, buffer = cv2.imencode('.jpg', image)
                producer.send('kafka-cctv', buffer.tobytes())
                producer.flush()
                os.remove('Sector1_help{}.jpg'.format(a))#파일 삭제
                a+=1
                i = 0
            cv2.putText(frame, "Help !", (xmin, ymin), cv2.FONT_ITALIC, 2, (0,0,255), 3)
            cv2.putText(gray, "Help !", (xmin, ymin), cv2.FONT_ITALIC, 2, (0, 0, 255), 3)

        xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3]) # data에 들어온 x,y 축 사각형 정보
        label = int(data[5])
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2) #초록색 창 띄우기
        cv2.putText(frame, class_list[label]+' '+str(round(confidence, 3)) + '%', (xmin, ymin), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)

        cv2.rectangle(gray, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # 초록색 창 띄우기
        cv2.putText(gray, class_list[label] + ' ' + str(round(confidence, 3)) + '%', (xmin, ymin), cv2.FONT_ITALIC, 1,(255, 0, 0), 2)

        results.append([[xmin, ymin, xmax-xmin, ymax-ymin], confidence, class_list[label]])

    end = datetime.datetime.now()
    total = (end - start).total_seconds()

    # fps = f'FPS: {1 / total:.2f}'
    # cv2.putText(frame, fps, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow('frame', frame)
    cv2.imshow('gray', gray)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
producer.close()
cv2.destroyAllWindows()