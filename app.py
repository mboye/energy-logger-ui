#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename
import os
from el4000 import *
from printers import *
import glob
import zipfile
import tempfile


app = Flask(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def upload_file():
    if 'zipFile' not in request.files:
        return redirect('/')

    file = request.files['zipFile']
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    csv_lines = process(save_path)
    response_data = '\n'.join(csv_lines)

    return Response(response_data, mimetype='text/csv')

class RecordingPrinter(BasePrinter):
    def __init__(self, filename, separator=','):
        self.separator = separator
        self.printed_header = False
        self.lines = []

    def print_data_header(self, t):
        pass

    def print_data(self, t, date):
        if not self.printed_header:
            line = self.separator.join(["timestamp"] + data.names)
            self.lines.append(line)
            self.printed_header = True

        line = '{1}{0}{2:5.1f}{0}{3:5.3f}{0}{4:5.3f}'.format(self.separator, date, *t)
        self.lines.append(line)

    def get_lines(self):
        return self.lines

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

        for filename in filenames:
            process_file(filename, printer, dt, data_only)

        return printer.get_lines()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
