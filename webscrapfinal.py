import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import re
import time

# Convert openTimeStr to dd-mm-yyyy format
def convert_opentimestr_to_date(opentimestr):
    now = datetime.now()

    if not opentimestr or not isinstance(opentimestr, str):
        return None

    opentimestr = opentimestr.lower()
    match = re.search(r"\d+", opentimestr)

    if "minute" in opentimestr or "hour" in opentimestr:
        return now.strftime("%d-%m-%Y")
    elif "day" in opentimestr and match:
        days = int(match.group())
        return (now - timedelta(days=days)).strftime("%d-%m-%Y")
    elif "month" in opentimestr and match:
        months = int(match.group())
        return (now - timedelta(days=30 * months)).strftime("%d-%m-%Y")
    elif "year" in opentimestr and match:
        years = int(match.group())
        return (now - timedelta(days=365 * years)).strftime("%d-%m-%Y")
    else:
        return now.strftime("%d-%m-%Y")

# Setup Selenium
options = Options()
# options.add_argument("--headless")  # Uncomment for headless mode
driver = webdriver.Chrome(options=options)

all_data = []

# Loop through pages
for page in range(1, 101):  # Because there are 100 pages
    print(f"Scraping page {page}")
    url = f"https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y&page={page}"
    driver.get(url)
    time.sleep(3)  # Adjust sleep if necessary

    # Execute JavaScript to get data
    script = "return window.PAGE_DATA && window.PAGE_DATA.index && window.PAGE_DATA.index.data;"
    rfq_data = driver.execute_script(script)

    if not rfq_data:
        print(f"No data found on page {page}")
        continue

    for item in rfq_data:
        rfq_id = item.get("rfqId")
        title = item.get("subject")
        buyer_name = item.get("buyerName")
        buyer_img_url = "https://ae01.alicdn.com/kf/" + item.get("portraitPath") if item.get("portraitPath") else ""
        inquiry_time = item.get("openTimeStr")
        quotes_left = item.get("rfqLeftCount")
        country = item.get("country")
        quantity = item.get("quantity")
        unit = item.get("quantityUnit")
        quantity = f"{quantity} {unit}".strip() if quantity and unit else quantity or ""
        tags = item.get("tags", [])
        email_confirmed = "Yes" if any(tag.get("tagName") == "emailConfirm" for tag in tags) else "No"
        experienced_buyer = "Yes" if item.get("rfqStarLevel", 0) > 0 else "No"
        complete_order = "Yes" if item.get("hasQuoEquity", False) else "No"
        typical_replies = "Yes" if item.get("quotesOrigin") else "No"
        interactive_user = "Yes" if item.get("quotesDiscount") else "No"
        inquiry_url = "https:" + item.get("url")
        inquiry_date = convert_opentimestr_to_date(inquiry_time)
        scraping_date = datetime.now().strftime("%d-%m-%Y")

        data = {
            "RFQ ID": rfq_id,
            "Title": title,
            "Buyer Name": buyer_name,
            "Buyer Image URL": buyer_img_url,
            "Inquiry Time": inquiry_time,
            "Quotes Left": quotes_left,
            "Country": country,
            "Quantity Required": quantity,
            "Email Confirmed": email_confirmed,
            "Experienced Buyer": experienced_buyer,
            "Complete Order via RFQ": complete_order,
            "Typical Replies": typical_replies,
            "Interactive User": interactive_user,
            "Inquiry URL": inquiry_url,
            "Inquiry Date": inquiry_date,
            "Scraping Date": scraping_date
        }

        all_data.append(data)

# Close browser
driver.quit()

# Save to DataFrame and export
df = pd.DataFrame(all_data)
df.to_csv("rfq_data_all_pages.csv", index=False)
print("Saved data for all pages.")
