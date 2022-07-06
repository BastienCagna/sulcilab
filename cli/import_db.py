"""
    Import BrainVisa database to Sulci Lab
    ======================================

    Example
    -------
    python manage.py import_db /neurospin/dico/data/bv_databases/human/archi Archi archi default_acquisition default_analysis 3.3 session1_manual Human

"""

from dico_toolbox.database import BVDatabase
from soma import aims
from tqdm import tqdm
from sulcilab.utils import split_label_name

from sulcilab.core import crud
from sulcilab.brainvisa import models as bmodels
import argparse


def import_db(path, name, spe, acq, ana, version, nom_name, verbose=False):
    #species = Species.objects.get(Q(en_name=spe) | Q(fr_name=spe))
    species = crud.get_all(db, bmodels.Species)

    if verbose:
        print('Reading the BV database...')
    db = BVDatabase(path)
    centers = db.list_all('center')
    subjects = db.list_all('subject')
    if verbose:
        print('{} subjects'.format(len(subjects)))

    nomenclature = crud.get_one_by(db, bmodels.Nomenclature, name=nom_name)#Nomenclature.objects.get(name=nom_name)
    try:
        database = crud.create(db, bmodels.BrainVisaDB, {'path':path, 'name':name})
        existing_subjects = []
    except:
        database = crud.get_one_by(db, bmodels.BrainVisaDB, name=name)
        if database.path != path:
            raise ValueError("{} already existing database do not match to path {}".format(database.name, path))
        existing_subjects = list(sub.name for sub in database.subjects)

    users = User.objects.filter(is_staff=True)
    if len(users):
        user = users[0]
    else:
        user = User.objects.create_user(username="SulciLab", password="icluSbaL", is_staff=True)
    print("Using user: ", user.username)

    if verbose:
        print('Scanning the subjects...')
    r = 0
    missing_labels = set()
    for sub in tqdm(list(sorted(subjects))):
        for h in ['L', 'R']:
            graph_f = None
            for center in centers:
                if graph_f:
                    break
                # for acq in acquisitions:
                #     if graph_f:
                #         break
                #     for ana in analyses:
                #         if graph_f:
                #             break
                #for version in ['3.3', '3.2', '3.1', '3.0']:
                graphs = db.get_from_template(
                    'morphologist_labelled_graph', center=center, subject=sub, hemi=h,
                    analysis=ana, acquisition=acq, version=version)
                if len(graphs) > 0:
                    # mesh_f = db.get_from_template(
                    #     'morphologist_mesh', type="white", center=center, subject=sub, hemi=h,
                    #     analysis=ana, acquisition=acq)
                    # if len(mesh_f) == 0:
                    #     continue
                    graph_f = graphs[0]
                    graph_v = version
                    graph_acq = acq
                    graph_ana = ana
                    graph_cent = center
                    graph = aims.read(graph_f)
                    break

            if graph_f:
                # if graph_f[-4:] != ".gii":
                #     print(sub)
                #     print(h)
                #     print(graph_f)
                #     self.stderr.write("Graph of {}, hemi {} is not a Gifti ({}). Skip this.".format(sub, h, graph_f))
                #     graph_f = None
                #     continue
                subject = Subject.objects.create(database=database, name=sub, center=graph_cent, acquisition=graph_acq, species=species)
                analysis = MorphologistAnalysis.objects.create(subject=subject, analysis=graph_ana)
                g = Graph.objects.create(path=graph_f, analysis=analysis, hemisphere=h, version=graph_v)
                labelset = LabelingSet.objects.create(graph=g, author=user, nomenclature=nomenclature)

                for v in graph.vertices():
                    if 'name' in v.keys():
                        lname, lhemi = split_label_name(v['name'])
                        left = lhemi == "L" or lhemi == "X"
                        right = lhemi == "R" or lhemi == "X"
                        fold = Fold.objects.create(
                            graph=g, vertex=v['index'])
                        try:
                            if left and right:
                                label = Label.objects.get(
                                    shortname=lname, left=left, right=right, nomenclatures__id=nomenclature.id)
                            elif left:
                                label = Label.objects.get(
                                    shortname=lname, left=left, nomenclatures__id=nomenclature.id)
                            elif right:
                                label = Label.objects.get(
                                    shortname=lname, right=right, nomenclatures__id=nomenclature.id)
                        except:
                            missing_labels.add(lname)
                            label = Label.objects.get(shortname="unknown", nomenclatures__id=nomenclature.id)
                            # print("cannot find label '{}' in {}".format(lname, nomenclature.name))
                            # for label in nomenclature.labels.all():
                            #     print(label.shortname)
                            # return
                        Labeling.objects.create(fold=fold, label=label, labeling_set=labelset)

                r += 1
            elif stdout:
                stdout.write("No valid graph for subject {}".format(sub))

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
    parser.add_argument('acq', type=str, help='Acquisition name')
    parser.add_argument('ana', type=str, help='Analysis name')
    parser.add_argument('vers', type=str, help='Graph version')
    parser.add_argument('sess', type=str, help='Labelling session')
    parser.add_argument('spe', type=str, help='Species')
    args = parser.parse_args()

    missing_labels, r = import_db(
        args['path'], args['name'], args['spe'], args['acq'], args['ana'], args['vers'], args['nom_name']
    )
    for label in missing_labels:
        print('Missing label {} in {}. Labelings set to "unknown".'.format(label, args['nom_name']))
    print('{} graphs added'.format(r))

