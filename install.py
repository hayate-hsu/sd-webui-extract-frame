import launch

if not launch.is_installed("cv2"):
    launch.run_pip("install opencv-python", "cv2")