
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

CSV_PATH = "grcdata.csv"
ROTATE_SECONDS = 120  # 2 minutes

def load_urls(path):
    urls = []
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.reader(f)
        for row in r:
            if row and row[-1].strip().lower().startswith(("http://", "https://")):
                urls.append(row[-1].strip())
    # Deduplicate preserving order
    seen = set()
    uniq = []
    for u in urls:
        if u not in seen:
            uniq.append(u); seen.add(u)
    return uniq

def main():
    urls = load_urls(CSV_PATH)
    if not urls:
        print("No valid URLs found.")
        return

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--kiosk")  # Linux/ChromeOS; on Windows use F11
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open first tab
    driver.get(urls[0])
    # Open the rest in new tabs
    for url in urls[1:]:
        driver.execute_script("window.open(arguments[0], '_blank');", url)

    tabs = driver.window_handles
    idx = 0
    while True:
        driver.switch_to.window(tabs[idx])
        # Optional refresh to keep content fresh
        driver.refresh()
        time.sleep(ROTATE_SECONDS)
        idx = (idx + 1) % len(tabs)

if __name__ == "__main__":
    main()
