from datetime import datetime
from flask import Flask, request, jsonify
import base64

from shared.SimpleWiki import SimpleWiki
from shared.settings import get_settings

application = Flask(__name__)
settings = get_settings()


@application.route('/')
def home():
  return "Nothing to see here. Use an actual action."


@application.route('/register_session', methods=['POST'])
def register_session():
  try:
    data = request.json

    if not all(k in data for k in ['code', 'title', 'description', 'imageData']):
      return jsonify({'error': 'Missing required fields'}), 400

    url = f"https://{settings['website']}"
    wiki = SimpleWiki(url)
    wiki.login(settings['user'], settings['password'])

    code = data['code']
    title = data['title']
    filename = f"Photo_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    image_data = data['imageData'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    upload_result = wiki.upload_file(image_bytes, filename, f'Affiche de la session : {title}')
    if upload_result['upload']['result'] != 'Success':
      raise Exception(upload_result)

    content = f"{data['description']}\n\n[[Fichier:{filename}|centré|cadre]]"
    update_page_result = wiki.create_or_update_page(code, content)
    rename_result = wiki.rename_page(code, title)

    return jsonify({
      'success': True,
      'redirect_url': f"{url}/index.php/{code}"
    })

  except Exception as e:
    return jsonify({'error': f'ERREUR: {str(e)}\nDetails: {e.__dict__}'}), 500


if __name__ == '__main__':
  application.run(debug=True)
