from django.core.management.base import BaseCommand, CommandError
from sulcilab import brainvisa
import matplotlib.colors as mcolors


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


class Command(BaseCommand):
    help = 'Setup database default data'

    def handle(self, *args, **options):
        self.add_colors(mcolors.TABLEAU_COLORS)
        self.add_colors(mcolors.CSS4_COLORS)

        # Set species
        for item  in brainvisa.DefaultSpecies:
            species = brainvisa.Species.objects.create(en_name=item.value[0][0], fr_name=item.value[0][1])
            species.save()
            self.stdout.write("New species: {}".format(species.en_name))

    def add_colors(self, new_colors):
        lcolors = {(c.red, c.green, c.blue, c.alpha)
                    : c for c in brainvisa.Color.objects.all()}
        for name, c in new_colors.items():
            c = hex_to_rgb(c)
            c = (c[0], c[1], c[2], 1)

            if not c in lcolors.keys():
                c_obj = brainvisa.Color(name=name, red=c[0],
                              green=c[1], blue=c[2], alpha=c[3])
                c_obj.save()
                #self.stdout.write("New color: {}".format(c_obj))
                lcolors[c] = c_obj
