from qreader import QReader
import cv2


qreader = QReader()

def scan(filename):

    image = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)

    decoded_text = qreader.detect_and_decode(image=image)

    print(decoded_text)
    if not decoded_text:
        return None, False

    try:
        return decoded_text[0], True
    except Exception:
        return None, False

