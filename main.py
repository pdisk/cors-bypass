import urllib.parse

from flask import Flask, Response, request
import requests

app = Flask(__name__)

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

@app.route('/news/<cat>')
def newsapi(cat):
    r = requests.post("https://inshorts.com/en/ajax/more_news", json={"category": cat})
    r = r.json().get("html")
    data = parse_html(r)
    return data


if __name__ == '__main__':
    app.run(debug=True)
