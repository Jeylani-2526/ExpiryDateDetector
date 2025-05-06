# Expiry Date Detector 🧴

This project detects expiry dates from product label images using OCR and determines whether the product is expired.



## 🔍 Features
- Detect expiry date using Tesseract OCR
- Works on common formats: `dd/mm/yyyy`, `yyyy-mm-dd`, etc.
- Compares with today's date and flags expired products

## 🛠️ Tech Stack
- Python
- OpenCV
- pytesseract
- Regex
- datetime

## 🚀 How to Run
1. Clone the repo
2. Install dependencies:
```

pip install -r requirements.txt

```
3. Run the detector:
```

python src/main.py sample\_images/sample1.jpg

```

## 📷 Sample Output
```

Detected Date: 2023-08-10
Status: ❌ This product is expired.

```

## 📂 Project Structure
- `sample_images/`: Example product label images
- `src/`: Main scripts and helper functions

## 👨‍💻 Author
- Abdalla Jeylani
