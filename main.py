import urllib.parse

from flask import Flask, Response, request
from flask_cors import CORS
import requests
import re
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "online"

@app.route('/get/<path:url>', methods=['GET'])
def proxy(url):
    url = urllib.parse.unquote(url)
    print(url)
    response = requests.get(url, stream=True)
    headers = {key: value for key, value in response.headers.items()}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Content-Disposition'] = f'attachment; filename="{url.split("/")[-1]}"'
    return Response(response.iter_content(chunk_size=1024), headers=headers,
                    content_type=response.headers['content-type'], )

def parse_html(r):
    titles = re.findall("<span itemprop=\"headline\">(.*?)\n?</span>", r)
    articles = re.findall("<div itemprop=\"articleBody\">(.*?)\n?</div>", r)
    images = re.findall('class="news-card-image".*?url\(\'(.*?)\'\)', r)
    authors = re.findall('news-card-author-time-in-title">\s+.*class="author">(.*?)</span>', r)
    dates = re.findall("<span class=\"date\">(.*?)\n?</span>", r)
    times = re.findall('<span class="time" itemprop="dateModified" content=".*" >(.*?)\n?</span>', r)
    # sources = re.findall('<span itemprop="description" content="([^"]*)"', r)
    results = []
    for i in range(len(articles)):
        data = {"title": titles[i],
                "article": articles[i],
                "author": authors[i],
                "image": images[i],
                "time": times[i],
                "date": dates[i],
                }
        results.append(data)
    return results

def parse_search_data(r):
    data = []
    for x in r:
        title = x.get("title")
        if not title:
            return
        article = x.get("summary")
        image = x.get("leadMedia").get("image").get("images").get("original")
        json = {"title": title, "article": article, "image": image}
        data.append(json)
    return data

@app.route('/news/get/<cat>')
def get_news(cat):
    r = requests.post("https://inshorts.com/en/ajax/more_news", json={"category": cat})
    r = r.json().get("html")
    data = parse_html(r)
    json = {"results": data}
    return json

@app.route('/news/search/<key>')
def search_news(key):
    r = requests.post("https://api.hindustantimes.com/api/articles/search",
                  json={"searchKeyword": key, "page": 1, "size": 25, "type": "story"})
    r = r.json().get("content")
    data = parse_search_data(r)
    json = {"results": data}
    return json


if __name__ == '__main__':
    app.run(debug=True)
