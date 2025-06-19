from datetime import datetime
import weasyprint


class PdfExporter:
  def __init__(self, page_contents: dict, internal_links: dict, image_dir: str, output_path: str = "wiki_export.pdf"):
    """
    :param page_contents: A dictionary containing the content of pages with page names
        as keys and their respective content as values.
    :param internal_links: A dictionary representing internal links between pages,
        with keys as link IDs and values as target page names.
    :param image_dir: Directory path containing images that may be included in
        the pages during export.
    :param output_path: Name of the output PDF file. Defaults to "wiki_export.pdf".
    """
    self.output_path = output_path
    self.page_contents = page_contents
    self.internal_links = internal_links
    self.image_dir = image_dir

  def fix_internal_links(self):
    """Fix internal links to point to the correct location in the PDF."""
    for page_title, content in self.page_contents.items():
      for a_tag in content.find_all('a', attrs={'data-internal-link': True}):
        link_id = a_tag.get('data-internal-link')
        target_page = self.internal_links.get(link_id)
        if target_page and target_page in self.page_contents:
          a_tag['href'] = f"#{target_page.replace(' ', '_')}"
        del a_tag['data-internal-link']

  def generate_pdf(self):
    """Generate a PDF from the crawled pages."""
    current_iso_date = datetime.now().astimezone().isoformat()
    html_parts = ['<!DOCTYPE html><html><head><meta charset="UTF-8">',
                  '<meta name="generator" content="https://github.com/Oaz/WikiPitch">',
                  '<meta name="dcterms.created" content="' + current_iso_date + '">',
                  '<style>',
                  'body { font-family: Arial, sans-serif; }',
                  '@page { margin: 1cm; }',
                  '.page { page-break-after: always; }',  # Ensure page break after each wiki page
                  '.page:last-child { page-break-after: avoid; }',  # Avoid page break after the last page
                  'a { text-decoration: none; color: #0645ad; }',
                  'a:hover { text-decoration: underline; }',
                  'a:visited { color: #0b0080; }',
                  'img { max-width: 100%; height: auto; }',
                  '</style></head><body>']

    self.fix_internal_links()
    pages_count = len(self.page_contents)
    for i, (page_title, content) in enumerate(self.page_contents.items()):
      if i == pages_count - 1:
        html_parts.append(f'<div class="page last-page" id="{page_title.replace(" ", "_")}">')
      else:
        html_parts.append(f'<div class="page" id="{page_title.replace(" ", "_")}">')
      html_parts.append(str(content))
      html_parts.append('</div>')
    html_parts.append('</body></html>')
    full_html = ''.join(html_parts)

    # Save HTML for debugging
    # with open(f"{self.output_path}.html", "w", encoding="utf-8") as f:
    #   f.write(full_html)

    print(f"Generating PDF: {self.output_path}")
    html = weasyprint.HTML(string=full_html)
    html.write_pdf(self.output_path)
    print(f"PDF generated successfully: {self.output_path}")
