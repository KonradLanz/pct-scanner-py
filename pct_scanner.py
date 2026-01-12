#!/usr/bin/env python3
"""
PCT-Scanner-Py v0.1 (AGPL-3.0)
Epson DS-80W USB | Brother DCP-9022CDW Netzwerk | Scanner-Auswahl + Config
"""
import sane
import zbarlight
from PIL import Image
import pytesseract
import click
import json
import os
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path.home() / ".config" / "pct-scanner.json"

def get_scanners():
    """SANE Scanner abrufen"""
    return [
        {"name": "brother", "device": "brother4:net1;dev0", "desc": "Brother DCP-9022CDW (Netzwerk)"},
        {"name": "epson_usb", "device": "epsonds:libusb:001:004", "desc": "Epson DS-80W USB"},
        {"name": "epson_esci2", "device": "epsonscan2:Epson DS-80W:001:004:esci2:usb:ES0180:358", "desc": "Epson DS-80W ESC/I-2 USB"},
        {"name": "epson_net", "device": "epsonscan2:networkscanner:esci2:network:192.168.1.8", "desc": "Epson Netzwerk"}
    ]

def load_config():
    """Config laden (default Brother)"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"scanner": "brother"}

def save_config(scanner):
    """Config speichern"""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"scanner": scanner}))

@click.command()
@click.option('--scanner', '-s', help='Scanner wählen (brother/epson_usb/epson_esci2/epson_net)')
@click.option('--test', is_flag=True, help='Nur Scanner-Info')
def main(scanner, test):
    config = load_config()
    
    scanners = get_scanners()
    if test:
        click.echo("📋 Verfügbare Scanner:")
        for s in scanners:
            click.echo(f"  {s['name']:12} {s['desc']}")
        return
    
    # Scanner-Auswahl
    if not scanner:
        scanner = click.prompt("Scanner wählen", type=click.Choice([s['name'] for s in scanners]), default=config['scanner'])
    
    dev_info = next(s for s in scanners if s['name'] == scanner)
    click.echo(f"🔍 Verwende: {dev_info['desc']}")
    
    save_config(scanner)  # Speichern
    
    # Scan
    dev = sane.open(dev_info['device'])
    dev.resolution = 300
    dev.mode = 'color'
    
    click.echo("📷 Scanne...")
    img = dev.scan()
    dev.close()
    
    # QR/OCR
    qr = zbarlight.scan_codes(['qrcode'], img)
    ocr = pytesseract.image_to_string(img, lang='deu')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pct_scan_{scanner}_{timestamp}.png"
    img.save(filename)
    
    click.echo(f"💾 {filename}")
    click.echo(f"📱 QR: {qr[0].decode() if qr else 'Kein QR'}")
    click.echo(f"📄 OCR Preview: {ocr[:100]}...")

if __name__ == "__main__":
    main()
