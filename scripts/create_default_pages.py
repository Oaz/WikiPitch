from shared.SimpleWiki import SimpleWiki
from shared.settings import get_settings

settings = get_settings()
WIKI_URL = f"https://{settings['website']}"
USERNAME = settings['user']
PASSWORD = settings['password']

try:
  wiki = SimpleWiki(WIKI_URL)
  wiki.login(USERNAME, PASSWORD)

  with open('codes.txt', 'r') as f:
    codes = f.readlines()

  for code in codes:
    code = code.strip()
    PAGE_TITLE = code
    PAGE_CONTENT = f"""Ce QR Code n'a pas encore été utilisé !
    
    [{WIKI_URL}/wikipitch/?code={code} Cliquez ici pour décrire votre session]."""

    result = wiki.create_or_update_page(PAGE_TITLE, PAGE_CONTENT)
    print(f"Created page for code {code}: {result}")

except Exception as e:
  print("Error:", str(e))
