#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename
import os
from el4000 import *
from printers import *
import glob
import zipfile
import tempfile
from time import sleep
import datetime
from os import environ
import os

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
        for data_point in process(tmp_filename):
            date_str = data_point[0].strftime('%Y-%m-%d %H:%M')
            power = data_point[1]
            kwh = joule_sum/(1000.0*3600)
            yield f'{date_str};{power:.1f};{kwh:.6f}\n'.encode('utf-8')
            joule_sum += power*60.0

    return Response(generate(), mimetype='text/csv')

class RecordingPrinter(BasePrinter):
    def __init__(self, filename, separator=','):
        self.separator = separator
        self.printed_header = False
        self.data_points = []

    def print_data_header(self, t):
        pass

    def print_data(self, t, date):
        effective_power = t.voltage * t.current * t.power_factor
        data_point = (date, effective_power)
        self.data_points.append(data_point)

    def read_data_points(self):
        ret = self.data_points
        self.data_points = []
        return ret

def process(zip_filename):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Extract ZIP file
        zip_ref = zipfile.ZipFile(zip_filename, 'r')
        zip_ref.extractall(tmp_dir)
        zip_ref.close()

        printer = RecordingPrinter('')
        dt = [datetime.datetime(1970, 1, 1)]
        data_only = True
        filenames = glob.glob(f'{tmp_dir}/**/*.BIN', recursive=True)

        data_points = []

        for filename in filenames:
            process_file(filename, printer, dt, data_only)
            data_points.extend(printer.read_data_points())

        os.unlink(zip_filename.name)
        return sorted(data_points)

if __name__ == '__main__':
    print(f'Starting energy-logger-ui {APP_VERSION}')
    app.run(host='0.0.0.0')
