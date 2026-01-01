## 종속성 패치
- 해당 프로그램은 raspberry pi 5의 bookwarm os 를 따릅니다.

```bash
sudo apt install libgstreamer1.0-dev gir1.2-gst-1.0
sudo apt install python3-gst-1.0
sudo apt install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
```

```bash
# python3
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-dev
# GUI 관련 패키지 (선택 사항이지만, 일부 OpenCV 기능에 필요할 수 있습니다.)
sudo apt install -y libqt5gui5 libqt5webkit5 libqt5test5

# 이 스크립트는 PEP 668 강제성을 무시하고 강력하게 전역으로 cv2를 설치합니다.
sudo pip install opencv-python --break-system-packages
sudo pip install opencv-contrib-python --break-system-packages
```

## 디버그 스크립트
- picamera 라이브러리의 debug 로그까지 확인할 수 있는 디버그 스크립트
```
GST_DEBUG=3 python record.py
```
