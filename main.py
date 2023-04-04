import urllib.parse

from flask import Flask, Response, request
import requests

app = Flask(__name__)


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

if __name__ == '__main__':
    app.run(debug=True)
