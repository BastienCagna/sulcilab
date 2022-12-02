"""
    Import BrainVisa database to Sulci Lab
    ======================================

    Example
    -------
    python manage.py import_db /neurospin/dico/data/bv_databases/human/archi Archi archi default_acquisition default_analysis 3.3 session1_manual Human

"""

from sulcilab.brainvisa.graph import GraphVersion
from sulcilab.database import SessionLocal
from sulcilab.utils.io import read_arg
from tqdm import tqdm
from sulcilab.utils.misc import split_label_name
from sulcilab.utils.database import BVDatabase

from sulcilab.core import crud
from sulcilab.brainvisa import Fold, Label, Database, Graph, Subject, Labeling, LabelingSet, Nomenclature, Species
from sulcilab.core import User, PUserCreate
from sulcilab.core.user import create_admin_user
from warnings import warn
import argparse


def import_graph(arg_file: str, db,
                 subject:Subject, acquisition:str, analysis:str, 
                 hemisphere:str, version:str, session:str,
                 nomenclature:Nomenclature, author: User, label_key='name'):
    _, nodes, _, _ = read_arg(arg_file)

    graph = crud.create(db, Graph,
        subject=subject,
        acquisition=acquisition,
        analysis=analysis,
        hemisphere="left" if hemisphere == "L" else "right",
        version=GraphVersion(version),
        session=session
    )

    labelset = crud.create(db, LabelingSet, author_id=author.id, graph=graph, nomenclature=nomenclature)

    tmp = list(filter(lambda label: label.shortname == "unknown", list(nomenclature.labels)))
    if len(tmp) == 0:
        raise RuntimeError("No unknown label")
    unknown_label = tmp[0]
    
    missing_labels = set()
    for v in nodes:
        if label_key in v.keys():
            lname, lhemi = split_label_name(v[label_key])
            left = lhemi == "L" or lhemi == "X"
            right = lhemi == "R" or lhemi == "X"
            fold = crud.create(db, Fold, graph=graph, vertex=v['index'], mesh_index=v['Tmtktri_label'])
            try:
                if left and right:
                    labels = crud.get_by(db, Label, shortname=lname, left=left, right=right)
                elif left:
                    labels = crud.get_by(db, Label, shortname=lname, left=left)
                else: # = elif right:
                    labels = crud.get_by(db, Label, shortname=lname, right=right)
                found = False
                for label in labels:
                    if nomenclature in label.nomenclatures:
                        found = True
                        break
                if not found:
                    raise RuntimeError("unknown label")
            except:
                missing_labels.add(lname)
                label = unknown_label
            crud.create(db, Labeling, fold=fold, label=label, labelingset=labelset)
    return graph, labelset, missing_labels


def import_db(path, name, fr_spe, acq, ana, version, graph_sess, nom_name, label_key='name', verbose=False):
    db = SessionLocal()
    species = crud.get_one_by(db, Species, fr_name=fr_spe)

    if verbose:
        print('Reading the BV database...')
    bvdb = BVDatabase(path)
    centers = bvdb.list_all('center')
    subjects = bvdb.list_all('subject')
    if verbose:
        print('{} subjects'.format(len(subjects)))

    nomenclature = crud.get_one_by(db, Nomenclature, name=nom_name)#Nomenclature.objects.get(name=nom_name)

    users = crud.get_by(db, User, is_admin=True)
    if len(users):
        user = users[0]
    else:
        user = create_admin_user(db, PUserCreate(username="admin", password="admin", email=""))
    print("Using user: ", user.username)

    database = crud.get_one_by(db, Database, name=name)
    if not database:
        database = crud.create(db, Database, path=path, name=name, owner_id=user.id, is_public=True)
        existing_subjects = []
    else:
        if database.path != path:
            raise ValueError("{} already existing database do not match to path {}".format(database.name, path))
        existing_subjects = list(sub.name for sub in database.subjects)

    if verbose:
        print('Scanning the subjects...')
    r = 0
    missing_labels = set()
    for sub in tqdm(list(sorted(subjects))):
        subject = crud.create(db, Subject, 
            database=database, 
            name=sub, 
            #center=graph_cent,
            species=species
        )
        for h in ['L', 'R']:
            graph_f = None
            for center in centers:
                if graph_f:
                    break
                graphs = bvdb.get_from_template(
                    'morphologist_labelled_graph', center=center, subject=sub, hemi=h,
                    analysis=ana, acquisition=acq, version=version)
                if len(graphs) > 0:
                    graph_f = graphs[0]
                    graph_v = version
                    graph_acq = acq
                    graph_ana = ana
                    graph_cent = center
                    break

            if graph_f:
                # try:
                _, _, miss_lbl = import_graph(graph_f, db, subject, graph_acq, graph_ana, h, graph_v, graph_sess, nomenclature, user, label_key)
                missing_labels.union(miss_lbl)
                r += 1
                # except:
                #     warn("Failed to load {}".format(graph_f))
            else:
                warn("No valid graph for subject {}".format(sub))

    return missing_labels, r


if __name__ == "__main__":
    """Import a BrainVisa database."""
    parser = argparse.ArgumentParser()
    # Positional arguments
    parser.add_argument(
        'path', type=str, help='Path to the BrainVISA database')
    parser.add_argument(
        'name', type=str, help='Name of the database')
    parser.add_argument(
        'nom_name', type=str, help='Name of the nomenclature')
    parser.add_argument('vers', type=str, help='Graph version')
    parser.add_argument('sess', type=str, help='Labelling session')
    parser.add_argument('spe', type=str, help='Species')
    parser.add_argument('--acq', dest="acq", type=str, default="default_acquisition", help='Acquisition name')
    parser.add_argument('--ana', dest="ana", type=str, default="default_analysis", help='Analysis name')
    parser.add_argument('-k', dest="label_key", type=str, default="name", help='Label key: "name" or "label"')
    args = parser.parse_args()

    missing_labels, r = import_db(
        args.path, args.name, args.spe, args.acq, args.ana, args.vers, args.sess, args.nom_name, args.label_key
    )
    for label in missing_labels:
        print('Missing label {} in {}. Labelings set to "unknown".'.format(label, args['nom_name']))
    print('{} graphs added'.format(r))

