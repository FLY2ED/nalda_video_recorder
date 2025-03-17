# NALDA 비디오 녹화기

NALDA 비디오 녹화기는 Python과 OpenCV를 이용한 간편한 웹캠 녹화 프로그램입니다. 사용자 친화적인 인터페이스와 다양한 필터 기능을 제공합니다.

## 주요 기능

### 비디오 녹화
- 60 FPS 고화질 비디오 녹화
- 사용자 지정 출력 폴더에 자동 저장
- 녹화 중 타이머 표시
- 녹화 파일명에 타임스탬프 자동 추가

### 이미지 필터 및 조정
- **밝기 조절**: 이미지 밝기를 실시간으로 조절 가능
- **대비 조절**: 이미지 대비(콘트라스트)를 실시간으로 조절 가능
- **좌우반전**: 카메라 이미지를 좌우로 반전시키는 기능
- **흑백모드**: 컬러 영상을 흑백으로 변환하는 기능
- **타임스탬프**: 현재 날짜와 시간을 화면에 표시하는 기능 (녹화에는 포함되지 않음)

### 사용자 인터페이스
- 직관적인 스타일의의 UI
- 실시간 비디오 미리보기
- 녹화 상태 및 시간 표시
- 설정 조절을 위한 버튼 및 슬라이더

### 단축키
- **Space**: 녹화 시작/중지
- **B/V**: 밝기 증가/감소
- **N/M**: 대비 증가/감소
- **F**: 좌우반전 활성화/비활성화
- **G**: 흑백모드 활성화/비활성화
- **T**: 타임스탬프 표시/숨김
- **Esc**: 프로그램 종료

## 특징
- OpenCV를 사용한 비디오 캡처 및 처리
- 60 FPS 녹화 지원
- DIVX 코덱을 사용한 효율적인 비디오 압축
- 실시간 이미지 필터링

## 설치 방법

1. Python 3.6 이상 설치
2. 필요한 패키지 설치:
```
pip install opencv-python pillow numpy
```
3. 프로그램 실행:
```
python main.py
```

## 사용 방법

1. 프로그램 실행 시 카메라 화면이 자동으로 표시됩니다.
2. 필요에 따라 밝기, 대비, 좌우반전, 흑백모드, 타임스탬프 등의 설정을 조정합니다.
3. "녹화 시작" 버튼을 클릭하거나 Space 키를 눌러 녹화를 시작합니다.
4. 녹화 중 상태 표시등이 빨간색으로 변하고 타이머가 표시됩니다.
5. 다시 "녹화 중지" 버튼 또는 Space 키를 눌러 녹화를 종료합니다.
6. 녹화된 파일은 "recordings" 폴더에 저장됩니다.

## 주의사항
- 카메라가 연결되어 있어야 합니다.
- 웹캠이 60 FPS를 지원하지 않는 경우에도 출력 파일은 60 FPS로 설정됩니다.
- 녹화 중 프로그램을 갑자기 종료하면 파일이 손상될 수 있습니다.
