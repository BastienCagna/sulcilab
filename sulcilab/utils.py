import os.path as op

BUILD_PATH = op.realpath(op.join(__file__, "..", "..", "build"))


def split_label_name(name):
    if name.endswith('_left'):
        if name[-6] == '.':
            return name[:-6], "L"
        return name[:-5], "L"
    elif name.endswith('_right'):
        if name[-7] == '.':
            return name[:-7], "R"
        return name[:-6], "R"
    return name, "X"
