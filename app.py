import os
from flask import Flask, request, jsonify, render_template
import b2
from pdf_generator import generate_pdf

app = Flask(__name__, static_folder='static', template_folder='templates')

b2.setup()


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
