"""OCR service using pytesseract to extract utility bill data locally."""

import io
import re

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None
import structlog

logger = structlog.get_logger(__name__)

def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess the image to improve OCR accuracy."""

    img = image.convert('L')

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_text_from_image(image: Image.Image) -> str:
    """Extract text from a PIL Image using pytesseract."""

    text_orig = pytesseract.image_to_string(image)

    processed_img = preprocess_image(image)
    text_processed = pytesseract.image_to_string(processed_img)

    return text_orig + "\n" + text_processed

def parse_utility_data(text: str) -> dict:
    """Extract kWh, cost, and dates using regex patterns."""
    data = {
        "kwh_usage": None,
        "total_cost": None,
        "confidence": 1.0,
        "parsed_footprints": {},
    }


    kwh_match = re.search(r'(?i)monthly\s*usage\s*(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*(?:kWh|kilowatt)', text)
    if not kwh_match:

        kwh_match = re.search(r'(?i)(?<!\d)(?!12,?450)(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*(?:kWh|kilowatt)', text)

    if kwh_match:
        try:
            data["kwh_usage"] = float(kwh_match.group(1).replace(',', ''))
        except ValueError:
            pass


    if data["kwh_usage"] is None:
        kwh_fallback = re.search(r'(?i)Total\s*Unit\s*(\d{1,5}(?:\.\d+)?)', text)
        if kwh_fallback:
            try:
                data["kwh_usage"] = float(kwh_fallback.group(1))
            except ValueError:
                pass

    cost_match = re.search(r'(?i)(?:total|amount due|balance).*?\$(\d{1,5}(?:\.\d{2})?)', text)
    if cost_match:
        try:
            data["total_cost"] = float(cost_match.group(1))
        except ValueError:
            pass

    if data["total_cost"] is None:
        cost_fallback = re.search(r'(?i)Total\s*Amt\s*Payable.*?\s*(\d{1,7}(?:\.\d{2})?)', text)
        if cost_fallback:
            try:
                data["total_cost"] = float(cost_fallback.group(1))
            except ValueError:
                pass



    for match in re.finditer(r'(?i)([a-z]+):?\s+(\d+\.\d+)\s+\S+\s*\(\d+%\)', text):
        category = match.group(1).lower()

        if category in ('rome', 'home', 'ome'):
            category = 'home'
        elif category in ('oe', 'diet', 'det'):
            category = 'diet'
        elif category in ('transport', 'trans', 'port'):
            category = 'transport'
        elif category in ('consumption', 'cons'):
            category = 'consumption'

        try:
            data["parsed_footprints"][category] = float(match.group(2))
        except ValueError:
            pass

    if data["kwh_usage"] is None:
        data["confidence"] -= 0.5
    if data["total_cost"] is None:
        data["confidence"] -= 0.3

    data["confidence"] = max(0.0, data["confidence"])
    return data

def process_document(file_bytes: bytes, filename: str) -> dict:
    """Process a document (PDF or Image) and extract utility data."""
    text = ""
    if filename.lower().endswith('.pdf'):
        if convert_from_bytes is None:
            logger.error("pdf2image not installed or Poppler missing. Cannot process PDF.")
            return {"error": "PDF processing not supported"}
        images = convert_from_bytes(file_bytes)
        for img in images:
            text += extract_text_from_image(img) + "\n"
    else:

        image = Image.open(io.BytesIO(file_bytes))
        text = extract_text_from_image(image)

    parsed = parse_utility_data(text)
    parsed["raw_text"] = text
    return parsed
