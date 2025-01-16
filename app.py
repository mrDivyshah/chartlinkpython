from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Scraper API! Available routes: /scrape"

@app.route('/scrape', methods=['GET'])
def scrape_data():
    url = 'https://chartink.com/screener/copy-idea-krishchess-combo-mbsanghavi'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'DataTables_Table_0'})

        if table:
            data = []
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                data.append([cell.text.strip() for cell in cells])
            return jsonify(data)
        else:
            return jsonify({'error': 'Table not found'})
    else:
        return jsonify({'error': 'Failed to fetch page'}), 500

if __name__ == '__main__':
    app.run(debug=True)
