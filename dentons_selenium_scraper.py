from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

def main():
    # Path to chromedriver.exe (assumed in same folder)
    CHROMEDRIVER_PATH = 'chromedriver.exe'  

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove if you want to see browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    url = 'https://www.dentons.com/en/our-people'
    driver.get(url)

    # Accept cookie banner if present (adjust selector as needed)
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Accept cookies']"))
        )
        cookie_button.click()
    except:
        pass  # No cookie banner or timeout

    # Scroll to load more profiles (adjust amount and timing as needed)
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    # Wait until profiles are loaded
    try:
        profile_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.profile-card"))  # Update selector as needed
        )
    except:
        print("❌ Profiles didn't load. Check CSS selector.")
        driver.quit()
        return

    print(f"Found {len(profile_cards)} profiles.")

    data = []
    for card in profile_cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, "h3, h4").text.strip()
            position = card.find_element(By.CSS_SELECTOR, ".position-class").text.strip()  # Replace with correct class
            office = card.find_element(By.CSS_SELECTOR, ".office-class").text.strip()      # Replace with correct class
            email = card.find_element(By.CSS_SELECTOR, "a.email-link").get_attribute("href").replace("mailto:", "").strip()
            data.append({
                "Name": name,
                "Position": position,
                "Office": office,
                "Email": email
            })
        except Exception as e:
            # If some info missing, skip that card
            continue

    if not data:
        print("⚠️ No profile data scraped.")
    else:
        with open("dentons_professionals.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Scraped {len(data)} profiles. Saved to dentons_professionals.csv")

    driver.quit()

if __name__ == "__main__":
    main()
