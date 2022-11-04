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
#  from sulcilab.brainvisa.label import NomLabelAssociation
from sulcilab.utils.misc import split_label_name
import numpy as np
import argparse
from sulcilab.core import crud
from sulcilab.database import sulcilab_cli, SessionLocal
from sulcilab.brainvisa import Nomenclature, Label
from sulcilab.data import Color
from sulcilab.utils.io import read_hie


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


@sulcilab_cli
def main(csv_f, nom_f):
    db = SessionLocal()

    # Read the labels infos (.csv file)
    labels = pd.read_csv(csv_f)

    # Read the nomenclature file that should contain all the labels
    hnames, colors, parents = read_hie(nom_f, flatten=True)

    # Split each name in name + hemi
    names, hemis = zip(*list(split_label_name(name) for name in hnames))

    # Load existing colors and create new in not already existing
    lcolors = {(c.red, c.green, c.blue, c.alpha) : c for c in crud.get_all(db, Color)}
    print("Load {} colors from the database".format(len(colors)))
    for c in colors:
        if not c in lcolors.keys():
            c_obj = crud.create(db, Color, red=c[0], green=c[1], blue=c[2], alpha=c[3])
            lcolors[c] = c_obj

    # Create the nomenclatures defined in the csv file
    nomenclatures = {}
    for k in labels.keys():
        if not k in ['shortname', 'fr', 'en', 'fr_desc', 'en_desc']:
            print("Creating new nomenclature: " + k)
            nomenclatures[k] = crud.create(db, Nomenclature, name=k)

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
            print("{} was not found in .hie file. Set random color, both hemisphere and no parent to this one.".format(shortname))
            hemi = 'X'
            color = lcolors[colors[np.random.randint(0, len(colors))]]
            ln = -1
            name = shortname
        else:
            hemi = hemis[ln]
            color = lcolors[colors[ln]]

        # If the label as already been added, skip
        if name in added_labels.keys():
            continue

        # Infer in which hemisphere the label is used (left, right or both)
        if hemi == "L":
            left = True
            right = ((name +"_right") in hnames) or ((name +"._right") in hnames)
        elif hemi == "R":
            left = ((name + "_left") in hnames) or ((name +"._left") in hnames)
            right = True
        else:
            left = True
            right = True

        # Create the label
        label = crud.create(db, Label,
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
        for nom in nomenclatures.values():
            # Check the CSV file to know if the label is used in this nomenclature
            if labels[nom.name][l] in ['x', 1, True, 'true', 'yes', 'oui']:
                # crud.create(db, NomLabelAssociation, {
                #     'label_id': label.id,
                #     'nomenclature_id': nom.id
                # })
                # label.nomenclatures_id
                nom.labels.append(label)
                # if label.nomenclatures_id is None:
                #     label.nomenclatures_id = [nom.id]
                # else:
                #     label.nomenclatures_id.append(nom.id)
    # db.flush()
    # for nom in nomenclatures.values():
    #     crud.update(db, Nomenclature, id=nom.id, labels_id=nom.labels_id)

    # Finally, set parents (ln is the index of the name in the .hie file)
    for ln, label in added_labels.values():
        if ln > -1 and parents[ln]:
            pname = split_label_name(parents[ln])[0]
            if pname in added_labels.keys():
                #crud.update(db, Label, id=label.id, parent_id=added_labels[pname][1].id)
                label.parent = added_labels[pname][1]
            else:
                print('Unknown parent "{}"'.format(pname))
    db.commit()

    print("Done")


if __name__ == "__main__":
    """Install labels and nomenclatures declared in a .csv file and present in .hie."""

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='.csv file')
    parser.add_argument('nom_file', type=str, help='.hie file')
    args = parser.parse_args()

    main(args.file, args.nom_file)

