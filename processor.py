from el4000 import *
import tempfile
import zipfile
from recording_printer import RecordingPrinter
from glob import glob


class Processor:
    def __init__(self, zip_file):
        self.zip_file = zip_file

    def process(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Extract ZIP file
            zip_ref = zipfile.ZipFile(self.zip_file, 'r')
            zip_ref.extractall(tmp_dir)
            zip_ref.close()

            printer = RecordingPrinter('')
            dt = [datetime.datetime(1970, 1, 1)]
            data_only = True
            filenames = glob(f'{tmp_dir}/**/*.BIN', recursive=True)

            data_points = []

            for filename in filenames:
                process_file(filename, printer, dt, data_only)
                data_points.extend(printer.read_data_points())

            os.unlink(self.zip_file.name)
            return sorted(data_points)
