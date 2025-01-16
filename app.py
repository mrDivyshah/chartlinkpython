from flask import Flask, request, jsonify, send_file
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import base64
import time
import os
from io import BytesIO

app = Flask(__name__)

# Helper function to set up the web driver
def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to scrape URLs from the screener page
def get_urls_and_indices(driver):
    results = []
    index = 1
    while True:
        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.ID, 'DataTables_Table_0'))
            )
            time.sleep(0.1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', id='DataTables_Table_0')
            links = table.find_all('a', class_='text-teal-700')

            for link in links:
                href = link.get('href')
                if 'fundamentals' in href:
                    href = href.replace('fundamentals', 'stocks')
                    full_link = f"https://chartink.com{href}"
                    results.append(full_link)

            next_button = driver.find_element(By.ID, 'DataTables_Table_0_next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print("No more pages or an error occurred:", e)
            break

    return results

# Function to scrape images from a specific link
def get_image_from_link(driver, url, timeframe, s_range, retries=3):
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ti"))
        )
        select_element = driver.find_element(By.ID, "ti")
        select_range_element = driver.find_element(By.ID, "d")

        h3_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h3[@style='margin: 0px;margin-left: 5px;font-size:20px']"))
        )
        company_name = h3_element.text

        # Select timeframe
        timeframe_mapping = {
            "1 day": "1", "2 days": "2", "3 days": "3", "5 days": "5", "10 days": "10",
            "1 month": "22", "2 months": "44", "3 months": "66", "4 months": "91",
            "6 months": "121", "9 months": "198", "1 year": "252", "2 years": "504",
            "3 years": "756", "5 years": "1008", "8 years": "1764", "All Data": "5000"
        }
        Select(select_element).select_by_value(timeframe_mapping.get(timeframe, "5000"))

        # Select range
        range_mapping = {
            "Daily": "d", "Weekly": "w", "Monthly": "m", "1 Minute": "1_minute",
            "2 Minute": "2_minute", "3 Minute": "3_minute", "5 Minute": "5_minute",
            "10 Minute": "10_minute", "15 Minute": "15_minute", "20 Minute": "20_minute",
            "25 Minute": "25_minute", "30 Minute": "30_minute", "45 Minute": "45_minute",
            "75 Minute": "75_minute", "125 Minute": "125_minute", "1 Hour": "60_minute",
            "2 Hour": "120_minute", "3 Hour": "180_minute", "4 Hour": "240_minute"
        }
        Select(select_range_element).select_by_value(range_mapping.get(s_range, "d"))

        # Click update button
        driver.find_element(By.ID, "innerb").click()

        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ChartImage"))
        )
        driver.switch_to.frame(iframe)

        for attempt in range(retries):
            try:
                body_html = driver.execute_script("return document.body.innerHTML;")
                img_match = re.search(r'<img[^>]*id="cross"[^>]*src="data:\s*image/[^;]+;base64,([^"]+)"', body_html)
                if img_match:
                    img_data_base64 = img_match.group(1)
                    return company_name, img_data_base64
            except Exception as e:
                time.sleep(5)

        return None, None

    except Exception as e:
        return None, None

# Flask route to scrape data
@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        screener_url = data.get('screener_url')
        timeframe = data.get('timeframe', 'All Data')
        s_range = data.get('range', 'Daily')

        driver = web_driver()
        driver.get(screener_url)
        results = get_urls_and_indices(driver)
        driver.quit()

        output_pdf = "screener_images.pdf"
        c = canvas.Canvas(output_pdf, pagesize=A4)
        a4_width, a4_height = A4

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_link, url, timeframe, s_range) for url in results]

            for future in as_completed(futures):
                company_name, image = future.result()
                if company_name and image:
                    temp_image_path = "temp_image.png"
                    image.save(temp_image_path)

                    image_ratio = image.width / image.height
                    a4_ratio = a4_width / a4_height
                    if image_ratio > a4_ratio:
                        scaled_width = a4_width
                        scaled_height = a4_width / image_ratio
                    else:
                        scaled_height = a4_height
                        scaled_width = a4_height * image_ratio

                    c.setPageSize((a4_width, scaled_height + 40))
                    c.drawCentredString(a4_width / 2, scaled_height + 30, company_name)
                    c.drawImage(temp_image_path, (a4_width - scaled_width) / 2, 20, width=scaled_width, height=scaled_height)
                    c.showPage()

        c.save()
        return send_file(output_pdf, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)})

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
