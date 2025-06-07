import qrcode
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
import csv


# Création d'un PDF avec les QR codes
# Paramétré par défaut pour le format Avery ETE016
# https://www.bureau-vallee.fr/256-etiquettes-ilc-blanc-35-x-49-mm-avery-208594.html

def create_qr_code(code, url):
  """Create QR code for a given code"""
  qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
  )
  qr.add_data(url)
  qr.make(fit=True)
  qr_image = qr.make_image(fill_color="black", back_color="white")
  temp_file = f"temp_{code}.png"
  qr_image.save(temp_file)
  return temp_file


def create_sticker_sheet(codes, output_file='stickers.pdf'):
  """Create PDF with QR codes arranged in a grid"""
  page_width, page_height = A5
  sticker_width = 35 * mm
  sticker_height = 49 * mm
  qr_code_size = sticker_width * 0.9
  text_height = (sticker_height - sticker_width) * 0.8
  margin = 4 * mm
  print(
    f"Page width: {page_width}, height: {page_height}, sticker width: {sticker_width}, sticker height: {sticker_height}, text height: {text_height}, margin: {margin}")

  cols = int((page_width - 2 * margin) // sticker_width)
  rows = int((page_height - 2 * margin) // sticker_height)
  codes_per_page = cols * rows

  c = canvas.Canvas(output_file, pagesize=A5)

  for i, (code, url) in enumerate(codes):
    print(f"Generating QR code for code {code} and {url}...")
    page = i // codes_per_page
    position = i % codes_per_page
    row = position // cols
    col = position % cols

    if position == 0 and i > 0:
      c.showPage()

    x = margin + col * sticker_width
    y = page_height - (margin + (row + 1) * sticker_height)

    qr_file = create_qr_code(code, url)
    c.drawImage(qr_file, x + (sticker_width - qr_code_size) / 2, y + text_height, width=qr_code_size,
                height=qr_code_size)

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(x + sticker_width / 2, y + text_height - 2 * mm, code)

    os.remove(qr_file)

  c.save()


if __name__ == "__main__":
  with open('codes.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f)
    next(csv_reader)
    codes = []
    for row in csv_reader:
      if row:
        codes.append((row[0], row[1]))

  if not codes:
    print("Warning: No codes were read from the CSV file")
    exit(1)

create_sticker_sheet(codes)
print("Generated QR code sticker sheet PDF")
