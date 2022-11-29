from enum import Enum
from typing import List
from warnings import warn
import nibabel as nb
import os.path as op
from os import makedirs
import sys
try:
    from soma import aims
except:
    print("soma is not installed")
import numpy as np


def aims_read_and_convert_to_nibabel(mesh_f):
    aims_mesh = aims.read(mesh_f)
    # header = aims_mesh.header()
    darrays = [None] * aims_mesh.size() * 2
    for i in range(aims_mesh.size()):
        vertices = np.array([x[:] for x in aims_mesh.vertex(i)]).tolist()
        polygons = np.array([x[:] for x in aims_mesh.polygon(i)]).tolist()
        darrays[i * 2] = nb.gifti.GiftiDataArray(vertices)
        darrays[i * 2 + 1] = nb.gifti.GiftiDataArray(polygons)
    return nb.GiftiImage(darrays=darrays)

def read_mesh(mesh_f):
    try:
        return nb.load(mesh_f)
    except:
        try:
            return aims_read_and_convert_to_nibabel(mesh_f)
        except:
            raise IOError("Cannot load " + mesh_f)

def check_dir(path):
    path = op.abspath(path)
    makedirs(path, exist_ok=True)
    return path


def decode(s: str):
    if isinstance(s, (list, tuple)):
        return list(decode(ss) for ss in s)
    splt = s.split(' ')
    if len(splt) > 1:
        return list(decode(s) for s in splt)
    else:
        if s.isnumeric():
            return int(s)
        try: 
            return float(s)
        except ValueError:
            return s
    # Shouldn't be there


def encode(data) -> str:
    pass

def text_to_dict(lines) -> dict:
    """
    bottom_point_number    13
    name                   S.Pe.C.inter._left
    point_number           139
    size                   152.901
    skeleton_label         1100
    ss_point_number        119
    CSF_volume             243.101
    GM_volume              1026.31
    LCR_volume             243.101
    Tal_boundingbox_max    57.5732 1.87628 -37.5335
    Tal_boundingbox_min    35.3252 -11.7119 -46.547
    Tmtktri_label          81
    bottom_label           81
    boundingbox_max        121 114 62
    boundingbox_min        104 102 53
    depth_direction        -0.919172 0.393857 0
    depth_direction_weight 15.411
    direction              -0.38656 -0.902143 -0.1916
    gravity_center         111.525 107.568 56.8849
    grey_surface_area      349.867
    hull_normal            -0.817782 0.25021 0.518292
    hull_normal_weight     83.9294
    index                  81
    label                  S.Pe.C.inter._left
    maxdepth               24.48
    mean_depth             21.7323
    mid_interface_voxels   266
    mindepth               0
    moments                152.901 18757.6 16447.3 8697.75 2745.45 1513.72 693.178 -591.078 -1000.19 648.006 2856.61 1127.7 545.406 -2499.66 360.795 150.018 521.349 -620.99 -1.73316 827.6
    normal                 -0.279836 0.312687 -0.9077
    other_label            81
    other_point_number     7
    refdepth_direction     -0.921212 0.378625 -0.089503
    refdirection           -0.367213 -0.922168 -0.121496
    refgravity_center      45.1591 -5.48262 -42.6448
    refhull_normal         -0.855322 0.294793 0.426054
    refmaxdepth            28.32
    refmean_depth          25.2446
    refmindepth            0
    refnormal              -0.244429 0.221701 -0.943982
    refsize                226.56
    refsurface_area        617.839
    rootsbassin            85
    ss_label               81
    surface_area           484.484
    talcovar               286982 -35175.6 -268724 -35175.6 5831.53 33044.7 -268724 33044.7 253391
    thickness_mean         3.74262
    thickness_std          0.542448
    white_surface_area     374.887
    """
    out = {}
    for l, line in enumerate(lines):
        if len(line):
            splt = list(filter(lambda s: len(s)>0, line[:-1].split(" ")))
            if len(splt) > 1:
                out[splt[0]] = decode(splt[1:]) if len(splt) > 2 else decode(splt[1])
            else:
                warn("The following line is invalid and was skipped while parsing:\n"+line)
    return out


def dict_to_text(data) -> dict:
    """

    """
    out = {}
    for l, line in enumerate(data):
        if len(line):
            splt = list(filter(lambda s: len(s)>0, line[:-1].split(" ")))
            if len(splt) > 1:
                out[splt[0]] = decode(splt[1:]) if len(splt) > 2 else decode(splt[1])
            else:
                warn("The following line is invalid and was skipped while parsing:\n"+line)
    return out


####
# Nomenclatures
##################
def list_names_and_colors(nom_node, parent=None):
    """ 
    
        Returns
        -------
        names: list of str
        colors: list of tuple (4,)
            r, g, b, a
        parents: 
    """
    names = []
    colors = []
    parents = []

    name = None
    if nom_node['name'] and nom_node['color']:
        name = nom_node['name']
        names.append(name)
        c = nom_node['color']
        colors.append((c[0], c[1], c[2], c[3] if len(c) > 3 else 255))
        parents.append(parent)

    for child in nom_node['children']:
        tmp_names, tmp_colors, tmp_parents = list_names_and_colors(
            child, name)
        names.extend(tmp_names)
        colors.extend(tmp_colors)
        parents.extend(tmp_parents)
    return names, colors, parents


def parse_nodes(lines):
    nodes = []
    curr_nom = None
    l = 0
    n_lines = len(lines)
    children_list_finished = False
    while l < n_lines:
        line = lines[l]
        if line.startswith("*BEGIN TREE fold_name"):
            if curr_nom:
                children, chd_dl = parse_nodes(lines[l:])
                curr_nom['children'] = children
                l += chd_dl
                line = lines[l]
            else:
                curr_nom = {
                    "name": None,
                    "color": None,
                    "label": None,
                    "children": []
                }
        elif line.startswith('name '):
            curr_nom['name'] = line[5:].strip()
        elif line.startswith('color '):
            curr_nom['color'] = list(int(s.strip()) for s in line[6:].split(' '))
        elif line.startswith('label '):
            curr_nom['label'] = line[6:].strip()
        if line.startswith('*END'):
            if curr_nom:
                nodes.append(curr_nom)
                curr_nom = None
            else:
                return nodes, l
        l += 1
    return nodes, l


def read_hie(file, flatten=False):
    with open(file, 'r') as f:
        hie, _ = parse_nodes(f.readlines())
    hie = {"name": "CorticalFoldArg", "color": None, "label": None, "children": hie}

    if flatten:
        # Return lists: names, colors, parents
        return list_names_and_colors(hie)
    else:
        # Return dictionnary with keys: "name", "color", label" and "children" for each node
        return hie


####
# Graphs
##########
class EdgeType(Enum):
    JUNCTION = 'junction'
    HULL_JUNCTION = 'hull_junction'
    CORTICAL = 'cortical'
    PLI_DE_PASSAGE = 'plidepassage'

class NodeType(Enum):
    FOLD = 'fold'
    HULL = 'hull'

def parse_item(lines: List[str], end_delimiter="*END", **init):
    """
    *BEGIN UEDGE junction 110 112
    point_number   28
    size           30.8002
    direction      0.541569 -0.448619 0.710946
    extremity1     79 186 65
    extremity2     85 182 70
    junction_label 405
    length         12.24
    maxdepth       10.64
    mindepth       1.1
    refdirection   0.506563 -0.314579 0.802767
    refextremity1  0.280397 77.1929 -45.88
    refextremity2  7.70961 73.8217 -38.9632
    reflength      14.04
    refmaxdepth    12.22
    refmindepth    1.28
    refsize        45.6379
    *END
    """
    for l, line in enumerate(lines):
        if line.startswith(end_delimiter):
            break
    item = text_to_dict(lines[1:l])
    for k, v in init.items():
        item[k] = v
    return item, l

def parse_arg(lines):
    l = 0
    n_lines = len(lines)
    nodes = []
    edges = []
    while l < n_lines:
        line = lines[l][:-1]
        if line.startswith('*BEGIN'):
            """ could be:
                *BEGIN GRAPH CorticalFoldArg
                *BEGIN NODE fold 1
                *BEGIN UEDGE hull_junction 195 28
                *BEGIN UEDGE cortical 60 168
                *BEGIN UEDGE plidepassage 256 57
                *BEGIN UEDGE junction 113 2
            """
            splt = line.split(' ')
            mode = splt[1]
            cat = splt[2]

            if mode == "GRAPH":
                metadata, offset = parse_item(lines[l:], end_delimiter="*BEGIN")
            elif mode == "NODE":
                if cat == "fold":
                    t = NodeType.FOLD
                elif cat == "hull":
                    t = NodeType.HULL
                else:
                    raise ValueError("Invalid node type {} line {}".format(cat, l))
                id = int(splt[3])
                node, offset = parse_item(lines[l+1:], id=id, type=t)
                nodes.append(node)
            elif mode == "UEDGE":
                if len(splt) < 5:
                    raise ValueError("Invalid edge declaration line {}. Missing arguments".format(l))
                a, b = int(splt[3]), int(splt[4])
                if cat == "hull_junction":
                    t = EdgeType.HULL_JUNCTION
                elif cat == "cortical":
                    t = EdgeType.CORTICAL
                elif cat == "plidepassage":
                    t = EdgeType.PLI_DE_PASSAGE
                elif cat == "junction":
                    t = EdgeType.JUNCTION
                else:
                    raise ValueError("Invalid edge type {} line {}".format(cat, l))
                edge, offset = parse_item(lines[l+1:], type=t, a=a, b=b)
                edges.append(edge)
            else:
                raise ValueError("Invalid mode {} line {}".format(mode, l))
            l += offset
        l += 1
    return metadata, nodes, edges


def read_arg(file, with_meshes=True):
    with open(file, 'r') as fp:
        metadata, nodes, edges = parse_arg(fp.readlines())
    if with_meshes:
        gii_f = op.join(file[:-3] + "data", "aims_Tmtktri.gii")
        if not op.isfile(gii_f):
            raise IOError(gii_f + " does not exist. Cannot load graph meshes.")
        gii = read_mesh(gii_f) #nb.load(gii_f)
        return metadata, nodes, edges, gii
    else:
        return metadata, nodes, edges, None


def write_arg(file, metadata, nodes, edges):
    raise NotImplementedError()
    # with open(file, 'w') as fp:
