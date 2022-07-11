


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

