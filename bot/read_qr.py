import imutils as imutils
from PIL import Image
from qreader import QReader
import cv2


qreader = QReader()

def scan(filename):
    img = cv2.imread(filename)

    # Rotate
    # Original_Image = Image.open(filename)
    # rotated_image1 = Original_Image.rotate(90, expand=1)
    # rotated_image1.save('NEW.jpg')

    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    decoded_text = qreader.detect_and_decode(image=image)

    print(decoded_text)
    if not decoded_text:
        return None, False

    try:
        return decoded_text[0], True
    except Exception:
        return None, False

