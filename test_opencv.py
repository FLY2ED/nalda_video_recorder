import cv2
import numpy as np

try:
    print("OpenCV 버전:", cv2.__version__)
    
    # 카메라 열기 시도
    print("카메라 열기 시도...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("에러: 카메라를 열 수 없습니다.")
    else:
        print("카메라가 성공적으로 열렸습니다.")
        
        # 프레임 읽기 시도
        ret, frame = cap.read()
        if ret:
            print("프레임 크기:", frame.shape)
            print("프레임 읽기 성공")
        else:
            print("프레임 읽기 실패")
        
        # 카메라 자원 해제
        cap.release()
        
except Exception as e:
    import traceback
    print(f"오류 발생: {e}")
    print(traceback.format_exc())

print("테스트 완료") 