import cv2
import time
import numpy as np
import os
import platform
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk

class NALDAVideoRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NALDA 비디오 녹화기")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f8f9fa")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 비디오 캡처 초기화
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("카메라를 열 수 없습니다.")
            self.root.quit()
            return
            
        # 비디오 속성
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = (self.frame_width, self.frame_height)
        
        # 비디오 설정
        self.cap_fps = self.cap.get(cv2.CAP_PROP_FPS)  # 카메라의 실제 FPS (참고용)
        self.fps = self.cap_fps if self.cap_fps > 0 else 60.0  # 카메라의 실제 FPS 사용, 0 이하일 경우 60으로 설정
        self.frame_interval = int(1000/self.fps)  # 프레임 간격 (밀리초)
        self.fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # DIVX 코덱 사용
        self.out = None
        
        # 프레임 타이밍 관련 변수
        self.recording_start_time = time.time()
        self.current_recording_time = 0
        self.frame_count = 0  # 프레임 수 초기화
        
        # 출력 디렉토리 생성
        self.output_dir = "recordings"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 필터 설정
        self.recording = False
        self.brightness = 0
        self.contrast = 1.0
        self.flip_horizontal = False
        self.grayscale = False
        self.show_timestamp = True
        
        # 토스 스타일 색상
        self.colors = {
            'primary': "#3182f6",  # 토스 파란색
            'secondary': "#68aaff",
            'background': "#ffffff",
            'panel_bg': "#f5f6f7",
            'text': "#333333",
            'text_light': "#787878",
            'success': "#4cd964",
            'danger': "#fc3d39",
            'warning': "#ffb800",
            'border': "#eaeaea"
        }
        
        # 폰트 설정
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="맑은 고딕", size=10)
        self.title_font = font.Font(family="맑은 고딕", size=14, weight="bold")
        self.subtitle_font = font.Font(family="맑은 고딕", size=12, weight="bold")
        self.status_font = font.Font(family="맑은 고딕", size=10)
        
        # UI 초기화
        self.setup_ui()
        
        # 영상 업데이트 시작
        self.update_frame()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 스타일 설정
        style = ttk.Style()
        style.configure("TFrame", background=self.colors['background'])
        style.configure("TLabel", background=self.colors['background'], font=self.default_font)
        style.configure("TButton", font=self.default_font)
        
        # 상단 프레임
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 앱 제목
        title_label = ttk.Label(top_frame, text="NALDA 비디오 녹화기", font=self.title_font, foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=10)
        
        # 녹화 상태 표시
        self.status_label = ttk.Label(top_frame, text="준비됨", font=self.status_font, foreground=self.colors['text'])
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # 중앙 프레임 (비디오 + 컨트롤)
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # 영상 표시 영역
        video_frame = ttk.Frame(center_frame, relief=tk.GROOVE, borderwidth=2)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 오른쪽 컨트롤 패널
        controls_frame = ttk.Frame(center_frame, relief=tk.GROOVE, borderwidth=2)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0), ipadx=10, ipady=10)
        
        # 설정 영역
        settings_label = ttk.Label(controls_frame, text="설정", font=self.subtitle_font, foreground=self.colors['primary'])
        settings_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # 밝기 조절
        brightness_frame = ttk.Frame(controls_frame)
        brightness_frame.pack(fill=tk.X, padx=10, pady=5)
        
        brightness_label = ttk.Label(brightness_frame, text="밝기:", width=10)
        brightness_label.pack(side=tk.LEFT)
        
        brightness_minus = ttk.Button(brightness_frame, text="-", width=3, command=self.decrease_brightness)
        brightness_minus.pack(side=tk.LEFT, padx=(0, 5))
        
        self.brightness_value = ttk.Label(brightness_frame, text="0", width=5)
        self.brightness_value.pack(side=tk.LEFT)
        
        brightness_plus = ttk.Button(brightness_frame, text="+", width=3, command=self.increase_brightness)
        brightness_plus.pack(side=tk.LEFT, padx=(5, 0))
        
        # 대비 조절
        contrast_frame = ttk.Frame(controls_frame)
        contrast_frame.pack(fill=tk.X, padx=10, pady=5)
        
        contrast_label = ttk.Label(contrast_frame, text="대비:", width=10)
        contrast_label.pack(side=tk.LEFT)
        
        contrast_minus = ttk.Button(contrast_frame, text="-", width=3, command=self.decrease_contrast)
        contrast_minus.pack(side=tk.LEFT, padx=(0, 5))
        
        self.contrast_value = ttk.Label(contrast_frame, text="1.0", width=5)
        self.contrast_value.pack(side=tk.LEFT)
        
        contrast_plus = ttk.Button(contrast_frame, text="+", width=3, command=self.increase_contrast)
        contrast_plus.pack(side=tk.LEFT, padx=(5, 0))
        
        # 토글 옵션들
        toggle_frame = ttk.Frame(controls_frame)
        toggle_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 좌우반전 토글
        self.flip_var = tk.BooleanVar(value=False)
        flip_check = ttk.Checkbutton(toggle_frame, text="좌우반전", variable=self.flip_var, command=self.toggle_flip)
        flip_check.pack(anchor=tk.W, pady=2)
        
        # 흑백모드 토글
        self.grayscale_var = tk.BooleanVar(value=False)
        grayscale_check = ttk.Checkbutton(toggle_frame, text="흑백모드", variable=self.grayscale_var, command=self.toggle_grayscale)
        grayscale_check.pack(anchor=tk.W, pady=2)
        
        # 타임스탬프 토글
        self.timestamp_var = tk.BooleanVar(value=True)
        timestamp_check = ttk.Checkbutton(toggle_frame, text="타임스탬프", variable=self.timestamp_var, command=self.toggle_timestamp)
        timestamp_check.pack(anchor=tk.W, pady=2)
        
        # 녹화 버튼
        record_frame = ttk.Frame(controls_frame)
        record_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.record_button = ttk.Button(record_frame, text="녹화 시작", command=self.toggle_recording)
        self.record_button.pack(fill=tk.X, pady=5)
        
        # 단축키 설명
        shortcuts_label = ttk.Label(controls_frame, text="단축키", font=self.subtitle_font, foreground=self.colors['primary'])
        shortcuts_label.pack(anchor=tk.W, padx=10, pady=(20, 5))
        
        shortcuts = [
            "Space: 녹화 시작/중지",
            "B/V: 밝기 +/-",
            "N/M: 대비 +/-",
            "F: 좌우반전",
            "G: 흑백모드",
            "T: 타임스탬프",
            "Esc: 종료"
        ]
        
        for shortcut in shortcuts:
            shortcut_label = ttk.Label(controls_frame, text=shortcut)
            shortcut_label.pack(anchor=tk.W, padx=20, pady=1)
        
        # 키보드 단축키 바인딩
        self.root.bind("<space>", lambda e: self.toggle_recording())
        self.root.bind("b", lambda e: self.increase_brightness())
        self.root.bind("v", lambda e: self.decrease_brightness())
        self.root.bind("n", lambda e: self.increase_contrast())
        self.root.bind("m", lambda e: self.decrease_contrast())
        self.root.bind("f", lambda e: self.toggle_flip())
        self.root.bind("g", lambda e: self.toggle_grayscale())
        self.root.bind("t", lambda e: self.toggle_timestamp())
        self.root.bind("<Escape>", lambda e: self.on_closing())
    
    def update_frame(self):
        try:
            # 카메라에서 프레임 읽기
            ret, frame = self.cap.read()
            
            if not ret:
                print("프레임을 읽을 수 없습니다. 프레임이 손실되었습니다.")
                return
            
            # 원본 프레임 복사 (녹화용)
            recording_frame = frame.copy()
            
            # 필터 적용
            frame = self.apply_filters(frame, for_display=True)  # UI 요소 포함
            recording_frame = self.apply_filters(recording_frame, for_display=False)  # UI 요소 제외
            
            # 녹화 중이면 저장
            if self.recording and self.out is not None:
                self.out.write(recording_frame)
                self.frame_count += 1  # 저장된 프레임 수 증가
                
                # 녹화 시간 업데이트 - 실제 경과 시간 사용
                self.current_recording_time = time.time() - self.recording_start_time
                minutes = int(self.current_recording_time) // 60
                seconds = int(self.current_recording_time) % 60
                self.status_label.configure(text=f"녹화 중... {minutes:02d}:{seconds:02d}", foreground=self.colors['danger'])
            
            # OpenCV BGR에서 RGB로 변환
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Tkinter에 표시하기 위해 PIL로 변환
            pil_img = Image.fromarray(frame_rgb)
            
            # 화면 크기에 맞게 리사이즈
            display_width = 800
            display_height = int(display_width * (self.frame_height / self.frame_width))
            pil_img = pil_img.resize((display_width, display_height), Image.LANCZOS)
            
            # PIL에서 ImageTk로 변환
            img_tk = ImageTk.PhotoImage(image=pil_img)
            
            # 라벨에 이미지 업데이트
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk  # 참조 유지
        except Exception as e:
            print(f"프레임 업데이트 중 오류: {e}")
            
        # 다음 프레임 업데이트 (FPS에 맞춰 간격 조정)
        self.root.after(self.frame_interval, self.update_frame)
    
    def apply_filters(self, frame, for_display=True):
        # 프레임에 선택된 필터 적용하기
        
        # 밝기와 대비 조절
        frame = cv2.convertScaleAbs(frame, alpha=self.contrast, beta=self.brightness)
        
        # 좌우 반전 적용 (활성화된 경우)
        if self.flip_horizontal:
            frame = cv2.flip(frame, 1)
        
        # 흑백 모드 적용 (활성화된 경우)
        if self.grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 일관된 녹화를 위해 BGR로 다시 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        
        # UI 요소는 디스플레이용 프레임에만 추가 (녹화용 프레임에는 추가하지 않음)
        if for_display:
            # 타임스탬프 오버레이 추가 (활성화된 경우)
            if self.show_timestamp:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 텍스트 크기 계산
                (text_width, text_height), _ = cv2.getTextSize(timestamp, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                
                # 텍스트 배경
                cv2.rectangle(frame, 
                            (10, self.frame_height - text_height - 30), 
                            (10 + text_width + 20, self.frame_height - 10), 
                            (255, 255, 255), -1)
                
                # 텍스트 테두리
                cv2.rectangle(frame, 
                            (10, self.frame_height - text_height - 30), 
                            (10 + text_width + 20, self.frame_height - 10), 
                            (240, 240, 240), 1)
                
                # 텍스트 추가
                cv2.putText(frame, timestamp, (20, self.frame_height - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 130, 255), 2)
            
            # 녹화 중인 경우 녹화 표시
            if self.recording:
                cv2.circle(frame, (self.frame_width - 30, 30), 15, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (self.frame_width - 70, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def toggle_recording(self):
        if not self.recording:
            # 녹화 시작
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.filename = os.path.join(self.output_dir, f"NALDA_recording_{timestamp}.avi")
            
            # 임시 비디오 파일 (원본 FPS로 저장)
            self.temp_filename = os.path.join(self.output_dir, f"NALDA_temp_{timestamp}.avi")
            self.out = cv2.VideoWriter(self.temp_filename, self.fourcc, self.fps, self.size)
            
            if not self.out.isOpened():
                self.show_error("녹화를 시작할 수 없습니다.")
                return
            
            # 녹화 타이밍 초기화
            self.recording_start_time = time.time()
            self.current_recording_time = 0
            self.frame_count = 0  # 프레임 수 초기화
            
            print(f"녹화 시작: {self.filename} (카메라 FPS: {self.cap_fps}, 녹화 FPS: {self.fps})")
            self.recording = True
            self.record_button.configure(text="녹화 중지")
            self.status_label.configure(text="녹화 중...", foreground=self.colors['danger'])
        else:
            # 녹화 중지
            if self.out is not None:
                self.out.release()
                self.out = None
                
                # 실제 녹화 시간 계산
                real_recording_time = time.time() - self.recording_start_time
                
                # 실제 FPS 계산 (프레임 수 / 실제 녹화 시간)
                real_fps = self.frame_count / real_recording_time if real_recording_time > 0 else self.fps
                
                print(f"녹화가 중지되었습니다. (총 프레임: {self.frame_count}, 총 녹화 시간: {real_recording_time:.2f}초, 실제 FPS: {real_fps:.2f})")
                
                # 실제 FPS로 비디오 파일 다시 생성
                print(f"올바른 재생 시간으로 비디오 파일 생성 중...")
                try:
                    # 임시 파일 열기
                    cap = cv2.VideoCapture(self.temp_filename)
                    if not cap.isOpened():
                        print(f"임시 파일을 열 수 없습니다: {self.temp_filename}")
                        return
                    
                    # 새 파일 생성 (올바른 FPS로)
                    out = cv2.VideoWriter(self.filename, self.fourcc, real_fps, self.size)
                    if not out.isOpened():
                        print(f"출력 파일을 생성할 수 없습니다: {self.filename}")
                        return
                    
                    # 모든 프레임 복사
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        out.write(frame)
                    
                    # 정리
                    cap.release()
                    out.release()
                    
                    # 임시 파일 삭제
                    if os.path.exists(self.temp_filename):
                        os.remove(self.temp_filename)
                        print(f"임시 파일 삭제: {self.temp_filename}")
                    
                    print(f"비디오 파일 생성 완료: {self.filename} (FPS: {real_fps:.2f})")
                    
                except Exception as e:
                    print(f"비디오 파일 변환 중 오류 발생: {e}")
                
                self.current_recording_time = real_recording_time
            
            self.recording = False
            self.record_button.configure(text="녹화 시작")
            self.status_label.configure(text="준비됨", foreground=self.colors['text'])
    
    def increase_brightness(self):
        self.brightness += 5
        self.brightness_value.configure(text=str(self.brightness))
        print(f"밝기: {self.brightness}")
    
    def decrease_brightness(self):
        self.brightness -= 5
        self.brightness_value.configure(text=str(self.brightness))
        print(f"밝기: {self.brightness}")
    
    def increase_contrast(self):
        self.contrast += 0.1
        self.contrast_value.configure(text=f"{self.contrast:.1f}")
        print(f"대비: {self.contrast:.1f}")
    
    def decrease_contrast(self):
        self.contrast -= 0.1
        if self.contrast <= 0.1:
            self.contrast = 0.1
        self.contrast_value.configure(text=f"{self.contrast:.1f}")
        print(f"대비: {self.contrast:.1f}")
    
    def toggle_flip(self):
        self.flip_horizontal = not self.flip_horizontal
        self.flip_var.set(self.flip_horizontal)
        print(f"좌우반전: {'켜짐' if self.flip_horizontal else '꺼짐'}")
    
    def toggle_grayscale(self):
        self.grayscale = not self.grayscale
        self.grayscale_var.set(self.grayscale)
        print(f"흑백모드: {'켜짐' if self.grayscale else '꺼짐'}")
    
    def toggle_timestamp(self):
        self.show_timestamp = not self.show_timestamp
        self.timestamp_var.set(self.show_timestamp)
        print(f"타임스탬프: {'켜짐' if self.show_timestamp else '꺼짐'}")
    
    def show_error(self, message):
        tk.messagebox.showerror("오류", message)
    
    def on_closing(self):
        if self.recording and self.out is not None:
            self.out.release()
        if self.cap is not None:
            self.cap.release()
        print("NALDA Video Recorder가 종료되었습니다.")
        self.root.destroy()

def main():
    try:
        root = tk.Tk()
        app = NALDAVideoRecorderGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print(f"프로그램 실행 중 오류가 발생했습니다: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()