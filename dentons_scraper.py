import requests
from bs4 import BeautifulSoup
import time
import csv

base_url = "https://www.dentons.com"
list_url = "https://www.dentons.com/en/our-professionals"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(list_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

profile_links = soup.select("a[href^='/en/']")

print("Found potential profiles:", len(profile_links))

seen = set()
data = []

for link in profile_links:
    href = link.get("href")
    name = link.get_text(strip=True)

    if not href or not name:
        continue
    if not href.startswith("/en/"):
        continue
    if any(x in href for x in [
        "/global-", "/terms", "/privacy", "/use-of-cookies", "legal-notices",
        "client-", "tax-", "web-", "contact", "our-professionals", "modern-slavery",
        "fraud", "regulation", "/footer", "/home", "/print"
    ]):
        continue

    # Avoid duplicates
    if name.lower() in seen:
        continue
    seen.add(name.lower())

    # Convert to full URL
    if not href.startswith("http"):
        href = base_url + href

    print(f"Scraping: {name} | {href}")

    try:
        prof_resp = requests.get(href, headers=headers)
        prof_soup = BeautifulSoup(prof_resp.text, "html.parser")

        email_tag = prof_soup.select_one("a[href^='mailto:']")
        email = email_tag.get("href").replace("mailto:", "") if email_tag else ""

        phone_tag = prof_soup.select_one("a[href^='tel:']")
        phone = phone_tag.get("href").replace("tel:", "") if phone_tag else ""

        office = ""
        office_tag = prof_soup.find("div", class_="office")
        if office_tag:
            office = office_tag.get_text(strip=True)

        position = ""
        position_tag = prof_soup.find("div", class_="position")
        if position_tag:
            position = position_tag.get_text(strip=True)

        practice_areas = ""
        pa_section = prof_soup.find("div", class_="practice-areas")
        if pa_section:
            practice_areas = ", ".join(li.get_text(strip=True) for li in pa_section.find_all("li"))

        data.append({
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Office": office,
            "Position": position,
            "Practice Areas": practice_areas,
            "Profile URL": href
        })

        time.sleep(2)  # polite delay
    except Exception as e:
        print(f"Error with {name}: {e}")

# Save to CSV
if data:
    with open("dentons_professionals.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print("Scraping completed. Data saved to dentons_professionals.csv")
else:
    print("No professional profiles were found.")
