import anatomist.api as ana
import time


a = ana.Anatomist()

# o = a.loadObject('/neurospin/dico/data/bv_databases/human/manually_labeled/archi/t1-1mm-1/001/t1mri/default_acquisition/default_analysis/segmentation/mesh/001_Lwhite.gii')
o = a.loadObject('/neurospin/dico/data/bv_databases/human/manually_labeled/archi/t1-1mm-1/001/t1mri/default_acquisition/default_analysis/segmentation/mesh/001_Lhemi.gii')


win = a.createWindow(
    "3D", geometry=[133, 93, 747, 516], options={"no_decoration": True}
)

win.addObjects([o], add_graph_nodes=True)
win.camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])
win.windowConfig(cursor_visibility=0)
