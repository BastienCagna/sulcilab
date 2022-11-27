import argparse
import os.path as op
import nibabel as nb
from sulcilab.utils.io import aims_read_and_convert_to_nibabel, check_dir
import shutil
from os import listdir


def copy_directory(in_dir, out_dir, recursive=True, verbose=False):
    out_dir = check_dir(out_dir)
    for file_name in listdir(in_dir):
        # construct full file path
        source = op.join(in_dir, file_name)
        destination = op.join(out_dir, file_name)
        # copy only files
        if op.isfile(source):
            shutil.copy(source, destination)
            if verbose:
                print('copied', file_name)
        elif recursive and op.isdir(source):
            copy_directory(source, destination)

            
def convert_mesh(in_f, out_f):
    gii = aims_read_and_convert_to_nibabel(in_f)
    nb.save(gii, out_f)

    
def convert_graph(graph_f, out_graph_f):
    dt_dir = graph_f[:-4] + ".data"
    out_dt_dir = check_dir(out_graph_f[:-4] + ".data")
    shutil.copy(graph_f, out_graph_f)
    copy_directory(dt_dir, out_dt_dir)
    fold_mesh_f = op.join(out_dt_dir, "aims_Tmtktri.gii")
    convert_mesh(fold_mesh_f, fold_mesh_f)


def graph_path(h, db, subname, acquisition="default_acquisition", analysis="default_analysis", version="3.1", session=None):
    graph_f = op.join(db, "subjects", subname, "t1mri", acquisition, analysis, "folds", version)
    if session:
        f = f'{h}{subname}_{session}.arg'
        graph_f = op.join(graph_f, session, f)
    else:
        graph_f = op.join(graph_f, f"{h}{subname}.arg")
    return graph_f


def convert_subject(db, subname, acquisition="default_acquisition", analysis="default_analysis", version="3.1", session="default_session_auto", new_session="default_session_auto_prepared"):
    for h in ['L', 'R']:
        graph_f = graph_path(h, db, subname, acquisition, analysis, version, session)
        new_graph_f = graph_path(h, db, subname, acquisition, analysis, version, new_session)
        if op.isfile(graph_f):
            print(f"Convert {graph_f} to {new_graph_f}")
            convert_graph(graph_f, new_graph_f)
        else:
            print(f"{graph_f} does not exist.")

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('db', type=str, help='Database')
    parser.add_argument('sub', type=str, help='Subject')
    parser.add_argument('--acq', dest='acq', type=str, default="default_acquisition", help='Acquisition')
    parser.add_argument('--ana', dest='ana', type=str, default="default_analysis", help='Analysis')
    parser.add_argument('--vers', dest='version', type=str, default="3.1", help='Graph version')
    parser.add_argument('--sess', dest='session', type=str, default="", help='Graph session')
    parser.add_argument('--nsess', dest='new_session', type=str, default="default_session_auto_prepared", help='New graph session')
    args = parser.parse_args()

    print("Database:", args.db)
    print("Subject:", args.sub)
    print("Acquisition:", args.acq)
    print("Analysis:", args.ana)
    print("Version:", args.version)
    print("Session:", args.session)
    print("New session:", args.new_session)
    convert_subject(
        args.db, args.sub,
        acquisition=args.acq, analysis=args.ana,
        version=args.version, session=args.session,
        new_session=args.new_session
    )


