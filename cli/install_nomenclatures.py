"""
    This command install the labels and nomenclature described in data/labels.csv
    It also use a .hie to get the colors.

    One line by label; Columns:
        - "shortname" is used to given label's shortnames
        - "fr", and "en" are used for french and english names
        - "fr_desc" and "en_desc" are used for french and english descriptions
        - other columns are use to create nomenclatures.
"""

# from django.core.management.base import BaseCommand, CommandError
# from sulcilab.brainvisa import Nomenclature, Color, Label
import pandas as pd
from tqdm import tqdm
from sulcilab.utils import split_label_name
from soma import aims
import numpy as np
import argparse
from sulcilab.core import crud
from sulcilab.data import models as dmodels
from sulcilab.data import schemas as dschemas
from sulcilab.brainvisa import models as bmodels
from sulcilab.brainvisa import schemas as bschemas
from sulcilab.database import SessionLocal, engine


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


def main(csv_f, nom_f):
    db = SessionLocal()

    # Read the laels infos (.csv file)
    labels = pd.read_csv(csv_f)

    # Read the nomenclature file that should contain all the labels
    hnames, colors, parents = list_names_and_colors(aims.read(nom_f))
    # Split each name in name + hemi
    names, hemis = zip(*list(split_label_name(name) for name in hnames))

    # Load existing colors and create new in not already existing
    lcolors = {(c.red, c.green, c.blue, c.alpha) : c for c in crud.get_all(db, dmodels.Color)}
    print("Load {} colors from the database".format(len(colors)))
    for c in colors:
        if not c in lcolors.keys():
            c_obj = crud.create(db, dmodels.Color, red=c[0], green=c[1], blue=c[2], alpha=c[3])
            lcolors[c] = c_obj

    # Create the nomenclatures defined in the csv file
    nomenclatures = {}
    for k in labels.keys():
        if not k in ['shortname', 'fr', 'en', 'fr_desc', 'en_desc']:
            print("Creating new nomenclature: " + k)
            nomenclatures[k] = crud.create(db, bmodels.Nomenclature, name=k)

    # Then add labels
    added_labels = {}
    for l in range(len(labels)):
        shortname = labels['shortname'][l]
        
        # Check if the label is in the nomenclature file
        found = False
        for ln, name in enumerate(names):
            if name == shortname:
                found = True
                break
        if not found:
            print("{} was not found in .hie file. Set random color and both hemisphere and no parent to this one.".format(shortname))
            hemi = 'X'
            color = lcolors[colors[np.random.randint(0, len(colors))]]
            ln = -1
            name = shortname
        else:
            hemi = hemis[ln]
            color = lcolors[colors[ln]]

        if name in added_labels.keys():
            continue
        if hemi == "L":
            left = True
            right = ((name +"_right") in hnames) or ((name +"._right") in hnames)
        elif hemi == "R":
            left = ((name + "_left") in hnames) or ((name +"._left") in hnames)
            right = True
        else:
            left = True
            right = True

        label = crud.create(db, bmodels.Label,# Label.objects.create(
            shortname=shortname, 
            left=left, 
            right=right, 
            color=color,
            fr_name=labels['fr'][l],
            en_name=labels['en'][l],
            fr_description=labels['fr_desc'][l],
            en_description=labels['en_desc'][l],
        )
        added_labels[name] = (ln, label)

        # Then add the label to nomenclatures that it belongs to
        # for nom in nomenclatures.values():
            # # self.stdout.write("Does {} ({}) is in {}?".format(label.shortname, l, nom.name))
            # # self.stdout.write("\t{}".format(labels[l][nom.name]))
            # if labels[nom.name][l] in ['x', 1, True, 'true', 'yes', 'oui']:
            #     nom.labels.add(label)

    # Finally, set parents
    # for ln, label in added_labels.values():
    #     if ln > -1 and parents[ln]:
    #         label.parent = added_labels[name][1]
    #         label.save()

    print("Done")


if __name__ == "__main__":
    """Install labels and nomenclatures declared in a .csv file and present in .hie."""

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='.csv file')
    parser.add_argument('nom_file', type=str, help='.hie file')
    args = parser.parse_args()

    main(args['file'], args['nom_file'])

