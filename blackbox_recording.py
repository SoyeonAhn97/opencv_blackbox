import cv2
import threading
import time
import os
import shutil

# 녹화 설정
recording_time = 60  # 녹화 시간 (초)
max_folder_size_mb = 500  # 최대 폴더 크기 (MB)

# 폴더 용량 계산 함수 (바이트 단위)
def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# 가장 오래된 폴더 삭제 함수
def delete_oldest_folder(parent_folder):
    folders = [
        os.path.join(parent_folder, f) for f in os.listdir(parent_folder)
        if os.path.isdir(os.path.join(parent_folder, f))
    ]
    oldest_folder = min(folders, key=os.path.getctime, default=None)
    if oldest_folder:
        try:
            shutil.rmtree(oldest_folder)
            print(f"폴더 삭제됨: {oldest_folder}")
        except Exception as e:
            print(f"폴더 삭제 실패: {oldest_folder}, 오류: {e}")

if __name__ == "__main__":
    # 웹캠 캡처 객체 생성
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # 녹화 설정
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"FPS: {fps}")

    recording = True
    last_minute = time.localtime().tm_min

    # out 변수 초기화
    out = None 

    while recording:
        # 1분마다 새로운 폴더 및 파일 생성
        if time.localtime().tm_min != last_minute:
            last_minute = time.localtime().tm_min

            # 현재 시간으로 폴더 생성
            current_hour = time.strftime("%Y%m%d_%H")
            output_folder = os.path.join("recordings", current_hour)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f"폴더 생성됨: {output_folder}")

            # 파일 이름 설정
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_folder, f"recording_{timestamp}.avi")

            # 기존 out 객체가 있다면 해제
            if out is not None:
                out.release()

            # 새로운 out 객체 생성
            out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        # 프레임 읽기 및 저장
        ret, frame = cap.read()
        if ret:
            # out 객체가 생성된 후 프레임 쓰기
            if out is not None: 
                out.write(frame)
            cv2.imshow('Webcam Recording', frame)

            # 'q' 키를 누르면 녹화 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                recording = False
                break

        # 폴더 용량 체크 및 삭제
        recording_folder = os.path.abspath("recordings")
        folder_size_bytes = get_folder_size(recording_folder)
        folder_size_mb = folder_size_bytes / (1024 * 1024)

        if folder_size_mb > max_folder_size_mb:
            delete_oldest_folder(recording_folder)

    # 녹화 종료
    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()