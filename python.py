from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from flask_cors import CORS

# Flask app setup
app = Flask(_name_)
CORS(app)  # Enable CORS for cross-origin requests

# Simple global variables for storing data
stored_texts = []
stored_embeddings = []

# Web Crawler to fetch content from URLs
class WebCrawler:
    def _init_(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def crawl_and_scrape(self, url: str):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for element in soup(['script', 'style', 'meta', 'header', 'footer']):
                element.decompose()
            return ' '.join(soup.stripped_strings)
        except requests.RequestException as e:
            return None

# Text Embedding Model using TF-IDF
class SimpleEmbeddingModel:
    def _init_(self):
        self.vectorizer = TfidfVectorizer()
        self.is_fitted = False

    def encode(self, texts):
        if not self.is_fitted:
            self.vectorizer.fit(texts)
            self.is_fitted = True
        return self.vectorizer.transform(texts).toarray()

# Initialize global instances
crawler = WebCrawler()
embedding_model = SimpleEmbeddingModel()

# Store embeddings and texts
def store_embeddings(texts):
    global stored_texts, stored_embeddings
    stored_texts = texts
    stored_embeddings = embedding_model.encode(texts)

# Perform similarity search
def search_query(query):
    if not stored_embeddings:
        return "No data ingested yet."

    query_embedding = embedding_model.encode([query])
    similarities = []
    for idx, embedding in enumerate(stored_embeddings):
        similarity = np.dot(query_embedding, embedding.T) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
        similarities.append((similarity, stored_texts[idx]))

    similarities.sort(reverse=True, key=lambda x: x[0])
    
    if similarities:
        return similarities[0][1]
    else:
        return "No relevant information found."

# Web Pipeline Class
class WebPipeline:
    def ingest_data(self, urls):
        texts = []
        for url in urls:
            text = crawler.crawl_and_scrape(url)
            if text:
                texts.append(text)
        store_embeddings(texts)

    def handle_query(self, query):
        return search_query(query)

# Initialize the pipeline
pipeline = WebPipeline()

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest():
    urls = request.json.get('urls', [])
    print(f"URLs received: {urls}")  # For debugging
    try:
        pipeline.ingest_data(urls)
        return jsonify({'status': 'success', 'message': 'Data ingested successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query', '')
    try:
        response = pipeline.handle_query(user_query)
        return jsonify({'status': 'success', 'response': response})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)