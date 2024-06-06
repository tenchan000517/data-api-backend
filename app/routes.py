# routes.py
from flask import Blueprint, jsonify, render_template
from app.scrape import scrape_all_data

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/scrape', methods=['GET'])
def scrape():
    data = scrape_all_data()
    return jsonify(data)
