import random
import string
import csv
from shared.settings import get_settings


def generate_unique_codes(count, length):
    codes = set()
    while len(codes) < count:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        codes.add(code)

    return sorted(list(codes))


def save_codes_to_files(codes, base_url, txt_filename='codes.txt', csv_filename='codes.csv'):
    with open(txt_filename, 'w') as f:
        for code in codes:
            f.write(f"{code}\n")

    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Code', 'URL'])  # Header row
        for code in codes:
            url = f"{base_url.rstrip('/')}/{code}"
            writer.writerow([code, url])


if __name__ == "__main__":
    settings = get_settings()

    codes = generate_unique_codes(
        count=settings['number_of_codes'],
        length=settings.get('code_length', 6)  # Use 6 as default if not specified
    )

    base_url = f"https://{settings['website']}/index.php/"
    save_codes_to_files(codes, base_url)
    print(f"Generated {len(codes)} unique codes and saved them to:")
    print("- codes.txt (codes only)")
    print("- codes.csv (codes with URLs)")