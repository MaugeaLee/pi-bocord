from picamera2 import Picamera2
from picamera2.encoders import Quality, H264Encoder
from picamera2.outputs import FfmpegOutput
import time


width=1920
height=1080
def record(width:int, height:int):
    # 초기 카메라 설정
    picam = Picamera2()
    config = picam.create_video_configuration(
        main={
            "size": (width, height),
            "format": "RGB888"
        },
        lores={"size": (640, 480)}, # 미리보기용 낮은 해상도 설정
        encode="main"
    )
    picam.configure(config)

    # Gstreamer 파이프 라인 설정
    GST_PIPELINE = (
        "appsrc name=bocord is-live=true format=3 ! "
        "videoconvert ! "
        "v4l2h264enc extra-controls=\"controls,video_bitrate=10000000;\" ! " # 비트레이트 설정 (10mbps)
        "h264parse ! "
        "splitmuxsink location=./temp/segment_%05d.mp4 max-size-time=60000000000 " # 60초 마다 segment 분할
        "muxer=mp4mux"
    )

    # Gstreamer 파이프라인에 보낼 인코더 지정
    encoder = H264Encoder(bitrate=10000000)
    output = FfmpegOutput("my_test.mp4") # 출력 파일 컨테이너 설정


    # Gstreamer 파이프라인에 연결하여 녹화 시작
    picam.start_preview()
    picam.start_recording(
        encoder=encoder, 
        # output=GST_PIPELINE, # output을 pipeline에 연결
        output=output,
        quality=Quality.VERY_HIGH
    )
    print("GStreamer를 통해 1분 단위 세그먼트 녹화를 시작합니다...")

    # 녹화 시간 유지
    time.sleep(10)

    # 녹화 종료
    picam.stop_recording()
    picam.stop_preview()
    picam.close()

    print("녹화가 종료되었습니다.")

if __name__ == "__main__":
    record(width=width, height=height)