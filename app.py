from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Helper function to set up the web driver
def check_chromedriver():
    try:
        # Path to chromedriver in the cdriver folder
        chromedriver_path = "./chromedriver.exe"
        
        # Chrome options
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        
        # Set up driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
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
