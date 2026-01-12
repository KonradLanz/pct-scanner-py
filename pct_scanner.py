#!/usr/bin/env python3
"""PCT-Scanner-Py: SANE/OCR/QR für Belege (AGPL-3.0)"""
import sane
import zbarlight
from PIL import Image
import pytesseract

def scan_and_process(device_name='brother4:net1;dev0'):
    dev = sane.open(device_name)
    img = dev.scan()
    dev.close()
    
    # QR + OCR
    qr_data = zbarlight.scan_codes(['qrcode'], img)
    ocr_text = pytesseract.image_to_string(img)
    
    print(f"QR: {qr_data}")
    print(f"OCR: {ocr_text[:200]}...")
    
if __name__ == "__main__":
    print("PCT Scanner ready!")
    scan_and_process()
