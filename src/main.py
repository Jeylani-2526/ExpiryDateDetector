import cv2
import pytesseract
import sys
from utils import extract_expiry_date, check_if_expired

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Jeylani\tesseract.exe"
# Optional: set tesseract path if it's not in your system PATH


def preprocess_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Image not found.")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def main(image_path):
    print(f"Processing: {image_path}")
    processed_img = preprocess_image(image_path)

    if processed_img is None:
        return

    text = pytesseract.image_to_string(processed_img)
    print("\n📝 OCR Text Extracted:\n", text)

    date = extract_expiry_date(text)
    if date:
        print(f"\n📆 Detected Expiry Date: {date.strftime('%Y-%m-%d')}")
        if check_if_expired(date):
            print("❌ Status: This product is expired.")
        else:
            print("✅ Status: This product is NOT expired.")
    else:
        print("⚠️ No valid expiry date found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
    else:
        main(sys.argv[1])
