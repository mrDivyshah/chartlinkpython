from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")  # Required in headless environments
    options.add_argument("--headless")  # Run Chrome in headless mode

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    
    driver.implicitly_wait(10)
    return driver

def check_chromedriver():
    try:
        driver = web_driver()
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
    app.run()
