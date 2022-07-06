import matplotlib.colors as mcolors

from sulcilab.core import models, crud
from sulcilab.database import SessionLocal, engine
from sulcilab.data.models import Color

models.Base.metadata.create_all(bind=engine)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def add_colors(new_colors):
    db = SessionLocal()
    lcolors = {(c.red, c.green, c.blue, c.alpha): c for c in crud.get_all(db, Color)}
    for name, c in new_colors.items():
        c = hex_to_rgb(c)
        c = (c[0], c[1], c[2], 1)

        if not c in lcolors.keys():
            color = {"name": name, "red": c[0], "green": c[1], "blue": c[2], "alpha": c[3]}
            c_obj = crud.create(db, Color, color)
            lcolors[c] = c_obj

def main():
    """ Import nammed color included in Matplotlib to the database. """
    add_colors(mcolors.TABLEAU_COLORS)
    add_colors(mcolors.CSS4_COLORS)


if __name__ == "__main__":
    main()
