import cv2
import pytesseract
import sys
import os
from utils import extract_expiry_date, check_if_expired

# Optional: set tesseract path if it's not in your system PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Jeylani\tesseract.exe"


def preprocess_image_multiple(image_path):
    """Apply multiple preprocessing techniques to improve OCR results"""
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Image not found.")
        return []

    # Store all processed versions
    processed_images = []

    # Original grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_images.append(("grayscale", gray))

    # Gaussian blur + adaptive threshold (original method)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    processed_images.append(("adaptive_threshold", thresh))

    # Otsu's thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(("otsu", otsu))

    # Increasing contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    processed_images.append(("contrast", contrast))

    # Morphological operations to clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    processed_images.append(("opening", opening))

    return processed_images


def run_ocr_with_config(image, config=''):
    """Run OCR with specific configuration"""
    try:
        # Basic configuration for improved accuracy
        base_config = '--oem 3 --psm 6'
        if config:
            base_config = f"{base_config} {config}"

        return pytesseract.image_to_string(image, config=base_config)
    except Exception as e:
        print(f"OCR error: {e}")
        return ""


def extract_text_from_image(image_path):
    """Extract text using multiple preprocessing methods and OCR configs"""
    processed_images = preprocess_image_multiple(image_path)

    if not processed_images:
        return ""

    all_text = ""

    # Try different OCR configurations
    ocr_configs = [
        '',  # Default
        '-c tessedit_char_whitelist=0123456789/.-: ',  # Focus on date characters
        '--psm 4',  # Assume single column of text
        '--psm 11',  # Sparse text with OSD
        '--psm 12'  # Sparse text without OSD
    ]

    # Save debug images if needed
    debug_dir = "debug_images"
    os.makedirs(debug_dir, exist_ok=True)

    for idx, (name, img) in enumerate(processed_images):
        # Save debug image
        cv2.imwrite(f"{debug_dir}/{os.path.basename(image_path)}_{name}.jpg", img)

        for config_idx, config in enumerate(ocr_configs):
            text = run_ocr_with_config(img, config)
            if text.strip():
                all_text += f"\n{text}"

                # Try to extract date from this segment
                date = extract_expiry_date(text)
                if date:
                    print(f"✓ Found date in {name} image with config {config_idx}")
                    return text, date

    return all_text, None


def main(image_path):
    print(f"Processing: {image_path}")

    # Extract text with various methods
    text, date = extract_text_from_image(image_path)

    if text:
        print("\n📝 OCR Text Extracted:\n", text)

    # If date was already found during OCR process
    if date:
        print(f"\n📆 Detected Expiry Date: {date.strftime('%Y-%m-%d')}")
        if check_if_expired(date):
            print("❌ Status: This product is expired.")
        else:
            print("✅ Status: This product is NOT expired.")
        return

    # If not found during initial processing, try again with the full text
    date = extract_expiry_date(text)
    if date:
        print(f"\n📆 Detected Expiry Date: {date.strftime('%Y-%m-%d')}")
        if check_if_expired(date):
            print("❌ Status: This product is expired.")
        else:
            print("✅ Status: This product is NOT expired.")
    else:
        print("⚠️ No valid expiry date found.")
        print("Try using a clearer image or different angle.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
    else:
        main(sys.argv[1])