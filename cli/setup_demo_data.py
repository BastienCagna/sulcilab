from django.core.management.base import BaseCommand, CommandError
from sulcilab import brainvisa
import matplotlib.colors as mcolors
from os import listdir, remove
import os.path as op
from sulcilab.management.commands.import_db import import_db
import json
import subprocess
import shutil


class Command(BaseCommand):
    help = 'Download demo dataset and install the databases'


    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'path', type=str, help='Path to the directory where the data will be downloaded')

    def handle(self, *args, **options):
        data_dir = op.join(options['path'], "demo_v0.0.1")
        source = ""

        # # Download .zip
        # zip_file = data_dir + ".zip"
        # cmd = 'wget --no-check-certificate  --content-disposition  {} -O {} '. \
        #     format(source, zip_file)

        # val = subprocess.call(cmd.split())
        # if val or not op.exists(zip_file):
        #     remove(data_dir)
        #     raise RuntimeError("An error occured while downloading test data from {} to {}.".
        #                        format(source, zip_file))

        # # Unzip and remove .zip
        # val = subprocess.call("unzip -o {} -d {}".format(zip_file, data_dir).split())
        # if val:
        #     # If it failed, remove the data directory otherwise next time the function will
        #     # not retry downloading
        #     shutil.rmtree(data_dir)
        #     raise RuntimeError("An error occured while decompressing test data from {} to {}.".
        #                     format(zip_file, data_dir))
        # remove(zip_file)

        # Import the databases
        for d in listdir(data_dir):
            db_dir = op.join(data_dir, d)
            spec_f = op.join(db_dir, "infos.json")
            if op.isdir(db_dir) and op.exists(spec_f):
                spec = json.load(open(spec_f, 'r'))
                self.stdout.write("\nInstalling " + spec['name'])
                import_db(db_dir, spec['name'], spec['species'], spec['acquisition'], spec['analysis'], spec['version'], spec['nomenclature'], self.stdout)
