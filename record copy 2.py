from picamera2 import Picamera2
from picamera2.encoders import Quality, H264Encoder
from picamera2.outputs import FfmpegOutput
import time
import cv2

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GstApp

WIDTH=1920
HEIGHT=1080
FPS = 60
BITRATE=10000 # x264 에서는 kbit 단위로 명시

GSTREAMER_PIPELINE = (
    # 1. appsrc: RAW 프레임을 받음
    'appsrc name=mysource is-live=true format=GST_FORMAT_TIME '
    f'caps=video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FPS}/1 ! '

    # 2. videoconvert: 색 공간/ 형식 변환
    'videoconvert ! video/x-raw,format=I420 ! '

    # 3. 인코딩: H.264로 압축
    f'x264enc tune=zerolatency bitrate={BITRATE} ! '

    # 4. h264parse: 스트림에 필요한 메타데이터 추가
    'h264parse ! '

    # 5. mp4mux: MP4 컨테이너에 H.264 스트림을 패키징
    'mp4mux name=mux ! '

    # 6. filesink 지정된 파일 이름으로 저장
    'filesink location=stream_record.mp4'
)
def record():
    global WIDTH, HEIGHT
    # -- Picamera2 설정 --
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (WIDTH, HEIGHT), "format": "YUV420"})
    picam2.configure(config)
    picam2.start()

    # -- Gstreamer 파이프 라인 설정 --
    Gst.init(None)
    pipeline = Gst.parse_launch(GSTREAMER_PIPELINE)
    appsrc = pipeline.get_by_name("mysource")

    # 파이프 라인을 PLAYING 상태로 전환
    pipeline.set_state(Gst.State.PLAYING)
    print(" --- 녹화 시작 --- ")
    start_time = time.time()
    try:
        # 현재 GStreamer 시간 (나노초 단위)을 계산
        timestamp = int((time.time() - start_time) * Gst.SECOND)
        while (time.time() - start_time) < 10:
            # record 1. Picamera2에서 RAW 프레임 캡처
            frame = picam2.capture_array()

            # record 2. Numpy 배열로 캡쳐된 frame을 Gstreamer 버퍼로 변환
            frame = frame.tobytes()
            buffer = Gst.Buffer.new_allocate(None, len(frame), None)
            buffer.fill(0, frame)
            buffer.offset = 0
            buffer.pts = timestamp # frame 마다 pt를 일일이 넣어줘야 한단다;;

            # ⭐️ 시간 스탬프 업데이트: 다음 프레임의 시간 스탬프는 이전 프레임 시간 + 프레임 당 간격
            # 프레임 당 간격 (Duration) = 1초 / FPS = 1 / 60 초
            duration = Gst.SECOND // FPS # Gst.SECOND는 1,000,000,000 나노초
            buffer.duration = duration
            timestamp += duration

            # record 3. appsrc에 버퍼 푸시
            appsrc.emit("push-buffer", buffer)
    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        # record finally 1. EOF (End of Stream) 전송: 파일 저장을 마무리 하기 위해 필수
        appsrc.emit("end-of-stream")
        print("EOF 신호 전송. 파일 마무리 대기 중 ...")
        
        # ** 안정적인 종료 로직
        bus = pipeline.get_bus()
        bus.timed_pop_filtered(
            Gst.CLOCK_TIME_NONE,
            Gst.MessageType.EOS | Gst.MessageType.ERROR
        )

        # record finally 2. 파이프라인을 종료 상태로 전환
        pipeline.set_state(Gst.State.NULL)

        # record finally 3. Picamera2 종료
        picam2.stop()
        print(" --- 녹화 종료 --- ")

    print("녹화가 종료되었습니다.")

if __name__ == "__main__":
    record()