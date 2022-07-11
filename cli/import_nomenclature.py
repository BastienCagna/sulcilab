"""
    A command to import a nomenclature file in the database.

    Typically use for: 
    /casa/host/src/brainvisa-share/master/nomenclature/hierarchy/sulcal_root_colors.hie
"""

from django.core.management.base import BaseCommand, CommandError
from sulcilab.brainvisa import Nomenclature, Color, Label
from soma import aims
from tqdm import tqdm
from sulcilab.utils.misc import split_label_name


def list_names_and_colors(nom_node, parent=None):
    names = []
    colors = []
    parents = []

    name = None
    if nom_node.has_key('name') and nom_node.has_key('color'):
        name = nom_node['name']
        names.append(name)
        c = nom_node['color']
        colors.append((c[0], c[1], c[2], c[3] if len(c) > 3 else 1))
        parents.append(parent)

    for child in nom_node.children():
        tmp_names, tmp_colors, tmp_parents = list_names_and_colors(
            child, name)
        names.extend(tmp_names)
        colors.extend(tmp_colors)
        parents.extend(tmp_parents)
    return names, colors, parents


class Command(BaseCommand):
    help = 'Import a nomenclature file to the database.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file', type=str, help='.hie file')

    def handle(self, *args, **options):
        # Get label names and colors
        names, colors, parents = list_names_and_colors(
            aims.read(options['file']))
        self.stdout.write("Listed {} names and {} colors.".format(
            len(names), len(colors)))

        # Create colors
        lcolors = {(c.red, c.green, c.blue, c.alpha) : c for c in Color.objects.all()}
        self.stdout.write(
            "Load {} colors from the database".format(len(colors)))
        for c in colors:
            if not c in lcolors.keys():
                c_obj = Color(red=c[0], green=c[1], blue=c[2], alpha=c[3])
                c_obj.save()
                # self.stdout.write("New color: {}".format(c))
                lcolors[c] = c_obj

        # Create nomenclature
        self.stdout.write("Creating new nomenclature")
        nom = Nomenclature.objects.create(name="BrainVISA 2018")

        # Create labels
        self.stdout.write("Adding {} labels".format(len(names)))
        labels = []
        already_sets = []
        for name, c, parent in tqdm(zip(names, colors, parents)):
            name, hemi = split_label_name(name)
            if name in already_sets:
                continue
            if hemi == "L":
                left = True
                right = (name +"_right") in names
            elif hemi == "R":
                left = (name + "_left") in names
                right = True
            else:
                left = True
                right = True

            if parent: 
                pname, _ = split_label_name(parent)
                parent = Label.objects.get(shortname=pname, nomenclature=nom)
            labels.append(Label.objects.create(
                shortname=name, left=left, right=right, parent=parent, nomenclature=nom, color=lcolors[c]))
            already_sets.append(name)

        self.stdout.write("Done")
