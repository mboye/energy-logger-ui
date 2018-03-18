#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, Response
from werkzeug.utils import secure_filename
import tempfile
from os import environ
from processor import Processor

app = Flask(__name__)
APP_VERSION = environ.get('APP_VERSION', 'unknown version')


@app.route('/')
def index():
    return render_template('index.html', APP_VERSION=APP_VERSION)


@app.route('/process', methods=['POST'])
def upload_file():
    if 'zipFile' not in request.files:
        return redirect('/')

    file = request.files['zipFile']
    tmp_filename = tempfile.NamedTemporaryFile(delete=False)
    file.save(tmp_filename)

    def generate():
        # Header
        yield 'timestamp;power;kwh_sum\n'.encode('utf-8')

        joule_sum = 0
        processor = Processor(tmp_filename)
        for data_point in processor.process():
            date_str = data_point[0].strftime('%Y-%m-%d %H:%M')
            power = data_point[1]
            kwh = joule_sum/(1000.0*3600)
            yield f'{date_str};{power:.1f};{kwh:.6f}\n'.encode('utf-8')
            joule_sum += power*60.0

    return Response(generate(), mimetype='text/csv')



if __name__ == '__main__':
    print(f'Starting energy-logger-ui {APP_VERSION}')
    app.run(host='0.0.0.0')
