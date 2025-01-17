from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
def web_driver():
    # Specify Chrome binary location
    chrome_binary_path = "/usr/bin/google-chrome"

    # Chrome options
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path  # Add this line
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Ensure headless mode for Render

    # Setup WebDriver with Service
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.implicitly_wait(10)
    return driver
# Helper function to set up the web driver
def check_chromedriver():
    try:
        driver = web_driver()
        
        # Test the driver by opening a simple URL
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        return {"status": "success", "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/check_chromedriver', methods=['GET'])
def check_driver():
    result = check_chromedriver()
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
