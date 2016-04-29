#!/usr/bin/env python3

from flask import (
    Flask, request, redirect, jsonify, render_template
)
from flask.ext.redis import FlaskRedis

from base62 import to_base62, from_base62

app = Flask(__name__)
redis = FlaskRedis(app)

app.config['DEBUG'] = True

KEY_URL_COUNT = 'url_count'
URL_PREFIX = 'url:'
SHORT_PREFIX = 'short:'


def init_redis():
    if not redis.get(KEY_URL_COUNT):
        redis.set(KEY_URL_COUNT, 0)


def get_shorten_url(request, code):
    host = request.headers['Host']
    return 'http://{}/{}'.format(host, code)


def shorten(url):
    code = redis.get(URL_PREFIX + url)
    if code:
        code = code.decode('u8')
    else:
        count = redis.get(KEY_URL_COUNT)
        redis.incr(KEY_URL_COUNT)
        code = int(count.decode('u8'))
        code = to_base62(code)
        redis.set(URL_PREFIX + url, code)
        redis.set(SHORT_PREFIX + code, url)
    return {
        'result': 'success',
        'shorten': get_shorten_url(request, code),
        'origin': url
    }


def get_origin(code):
    return redis.get(SHORT_PREFIX + code)


def normalize(url):
    if url.find('://') == -1:
        url = 'http://' + url
    return url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/404')
def missing():
    return render_template('missing.html')


@app.route('/', methods=['POST'])
def create_shorten():
    url = request.form['url']
    url = normalize(url)
    result = shorten(url)
    return render_template('result.html', result=result)


@app.route('/<short>')
def goto(short):
    url = get_origin(short)
    if url:
        return redirect(url)
    else:
        return redirect('/404')


@app.route('/debug')
def debug():
    count = int(redis.get(KEY_URL_COUNT) or 0)
    urls = []
    for s in redis.keys(SHORT_PREFIX + '*'):
        url = redis.get(s).decode('u8')
        code = redis.get(URL_PREFIX + url).decode('u8')
        short = get_shorten_url(request, code)
        urls.append((s.decode('u8'), url, short))
    return render_template('debug.html', count=count, urls=urls)


if __name__ == '__main__':
    init_redis()
    app.run()
