import os
import tempfile
from collections import deque
from urllib.parse import urlparse, urljoin, unquote, quote
import requests
from bs4 import BeautifulSoup


def get_page_name_from_anchor(href):
  if not href or href.startswith('#') or ':' in href.split('/')[0]:
    return None
  parsed_url = urlparse(href)
  if parsed_url.netloc:
    return None
  path = parsed_url.path
  if path == '/index.php':
    return None
  if 'index.php' not in path:
    return None
  page_name = path.replace('/index.php/', '').replace('_', ' ')
  if '?' in page_name:
    page_name = page_name.split('?')[0]
  if page_name.startswith('Fichier:'):
    return None
  return unquote(page_name)


class WikiDownloader:
  def __init__(self, website, start_page):
    """
    Initialize the Wiki Downloader.

    Args:
        website (str): Domain name of the MediaWiki site
        start_page (str): Title of the starting page
    """
    self.session = requests.Session()
    self.website = website
    self.start_page = start_page
    self.visited_pages = set()
    self.pages_to_crawl = deque([start_page])
    self.page_contents = {}
    self.page_urls = {}
    self.internal_links = {}
    self.image_dir = tempfile.mkdtemp()
    self.image_map = {}

  def download_image(self, image_url):
    """Download an image and store it locally."""
    try:
      if not image_url.startswith(('http://', 'https://')):
        image_url = urljoin(f"https://{self.website}", image_url)
      if image_url in self.image_map:
        return self.image_map[image_url]
      parsed_url = urlparse(image_url)
      filename = os.path.basename(parsed_url.path)
      local_path = os.path.join(self.image_dir, filename)
      count = 1
      while os.path.exists(local_path):
        name, ext = os.path.splitext(filename)
        local_path = os.path.join(self.image_dir, f"{name}_{count}{ext}")
        count += 1
      response = self.session.get(image_url, stream=True)
      response.raise_for_status()
      with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
          f.write(chunk)
      self.image_map[image_url] = local_path
      return local_path

    except Exception as e:
      print(f"Error downloading image {image_url}: {e}")
      return None

  def process_images(self, content_div):
    """Process images in the content and download them for PDF inclusion."""
    if not content_div:
      return content_div
    for img_tag in content_div.find_all('img'):
      src = img_tag.get('src', '')
      if not src:
        continue
      local_path = self.download_image(src)
      if local_path:
        img_tag['src'] = f"file://{local_path}"
    return content_div

  def get_page_content(self, page_title):
    """Retrieve the content of a page in printable format."""
    url = f"https://{self.website}/index.php?title={quote(page_title.replace(' ', '_'))}"
    try:
      response = self.session.get(url)
      response.raise_for_status()
      soup = BeautifulSoup(response.text, 'html.parser')
      content_div = soup.find('div', {'id': 'mw-content-text'})
      if not content_div:
        content_div = soup.find('div', {'class': 'mw-body-content'})
      if not content_div:
        print(f"Warning: Could not find content for page {page_title}")
        return None
      content_div = self.sanitize_content(content_div, soup)
      title_elem = soup.new_tag('h1')
      title_elem.string = page_title
      content_div.insert(0, title_elem)
      self.page_urls[page_title] = url
      content_div = self.process_images(content_div)
      return content_div
    except requests.RequestException as e:
      print(f"Error retrieving page {page_title}: {e}")
      return None

  def sanitize_content(self, content_div, soup):
    printfooter = content_div.find('div', {'class': 'printfooter'})
    if printfooter:
      printfooter.decompose()
    for editsection in content_div.find_all('span', {'class': 'mw-editsection'}):
      editsection.decompose()
    for file_desc in content_div.find_all('a', {'class': 'mw-file-description'}):
      file_desc.unwrap()
    return content_div

  def extract_wiki_links(self, content_div, current_page):
    """Extract wiki links from content and return processed content."""
    if not content_div:
      return content_div, []
    links = []
    for a_tag in content_div.find_all('a'):
      href = a_tag.get('href', '')
      page_name = get_page_name_from_anchor(href)
      if page_name is None:
        continue
      if page_name != current_page and page_name not in self.visited_pages:
        links.append(page_name)
      link_id = f"link-{len(self.internal_links)}"
      self.internal_links[link_id] = page_name
      a_tag['data-internal-link'] = link_id
    return content_div, links

  def crawl_pages(self):
    """Crawl wiki pages starting from the start page."""
    print(f"Starting crawl from page: {self.start_page}")
    while self.pages_to_crawl:
      current_page = self.pages_to_crawl.popleft()
      if current_page in self.visited_pages:
        continue
      print(f"Crawling page: {current_page}")
      self.visited_pages.add(current_page)
      content_div = self.get_page_content(current_page)
      if not content_div:
        continue
      processed_content, new_links = self.extract_wiki_links(content_div, current_page)
      self.page_contents[current_page] = processed_content
      for link in new_links:
        if link not in self.visited_pages:
          self.pages_to_crawl.append(link)
    print(f"Crawling complete. Visited {len(self.visited_pages)} pages.")
