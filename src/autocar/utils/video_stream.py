import cv2

def gen_mjpeg(camera, fps=24):
    """Generates the MJPEG stream from a camera object."""
    while True:
        frame = camera.read()
        if frame is None:
            continue
        ok, jpg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
