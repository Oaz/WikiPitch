#!/usr/bin/env python3
import os
import shutil
from scripts.PdfExporter import PdfExporter
from scripts.WikiDownloader import WikiDownloader
from shared.settings import get_settings

settings = get_settings()

downloader = WikiDownloader(
  website=settings['website'],
  start_page='Accueil'
)
downloader.crawl_pages()

exporter = PdfExporter(
  downloader.page_contents,
  downloader.internal_links,
  downloader.image_dir,
  output_path=f"{settings['website']}.pdf"
)
exporter.generate_pdf()

if os.path.exists(downloader.image_dir):
  shutil.rmtree(downloader.image_dir)
