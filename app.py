import os
import math
import time
import shutil
import re
from flask import Flask, request, jsonify, render_template
from pinterest_dl import PinterestDL
from fpdf import FPDF
from scale_img import scale_and_position_image, FpdfBoundingBox
import b2

app = Flask(__name__, static_folder='static', template_folder='templates')

b2.setup()

BASE_DIR = "/app"
IMAGES_BASE = os.path.join(BASE_DIR, "images")
PDFS_BASE = os.path.join(BASE_DIR, "pdfs")

os.makedirs(IMAGES_BASE, exist_ok=True)
os.makedirs(PDFS_BASE, exist_ok=True)


def parse_pinterest_url(url):
    """Extract username and board from Pinterest URL."""
    match = re.search(r'pinterest\.com/([^/]+)/([^/]+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def generate_pdf(url, num_images, draw_borders, images_in_row, images_in_col, margin):
    username, board = parse_pinterest_url(url)
    if not username or not board:
        raise ValueError("Invalid Pinterest URL")

    timestamp = int(time.time())
    folder_name = f"{username}_{board}"
    pdf_name = f"{username}_{board}_{timestamp}.pdf"

    img_folder = os.path.join(IMAGES_BASE, folder_name)
    pdf_folder = os.path.join(PDFS_BASE, folder_name)
    os.makedirs(img_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)

    try:
        # Use longer delay for large batches to avoid rate limiting
        delay = 0.5 if num_images > 50 else 0.2

        PinterestDL.with_api(max_retries=5).scrape_and_download(
            url=url,
            output_dir=img_folder,
            num=num_images,
            delay=delay
        )

        # Filter for valid image files only (exclude videos, etc.)
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = [
            f for f in os.listdir(img_folder)
            if os.path.isfile(os.path.join(img_folder, f))
            and os.path.splitext(f)[1].lower() in valid_extensions
        ]

        if not images:
            raise ValueError("No images downloaded")

        pdf = FPDF()
        _h = pdf.eph
        _w = pdf.epw

        images_per_page = images_in_row * images_in_col
        cell_w = _w / images_in_row
        cell_h = _h / images_in_col

        pages = math.ceil(len(images) / images_per_page)
        img_idx = 0

        for p in range(pages):
            pdf.add_page()
            for row in range(images_in_col):
                for col in range(images_in_row):
                    if img_idx >= len(images):
                        break
                    x = col * cell_w + margin
                    y = row * cell_h + margin
                    box = FpdfBoundingBox(x=x, y=y, w=cell_w - (2 * margin), h=cell_h - (2 * margin))
                    if draw_borders:
                        pdf.set_draw_color(0, 0, 0)
                        pdf.rect(**box, style="D")
                    scale_and_position_image(pdf, os.path.join(img_folder, images[img_idx]), box, "C")
                    img_idx += 1

        pdf_path = os.path.join(pdf_folder, pdf_name)
        pdf.output(pdf_path)

        # Upload to B2 and get download URL
        remote_name = f"{folder_name}/{pdf_name}"
        b2.upload_file(pdf_path, remote_name)
        download_url = b2.get_download_url(remote_name)

        # Cleanup local PDF
        os.remove(pdf_path)

        return download_url

    finally:
        # Cleanup images
        if os.path.exists(img_folder):
            shutil.rmtree(img_folder)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.json
        url = data.get('url', '')
        num_images = int(data.get('num_images', 10))
        draw_borders = bool(data.get('draw_borders', True))
        images_in_row = int(data.get('images_in_row', 2))
        images_in_col = int(data.get('images_in_col', 3))
        margin = float(data.get('margin', 5))

        download_url = generate_pdf(url, num_images, draw_borders, images_in_row, images_in_col, margin)

        return jsonify({'success': True, 'pdf_path': download_url})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
