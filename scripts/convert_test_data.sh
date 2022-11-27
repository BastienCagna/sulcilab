data_path=$1 #"/home/bastien/cloud/bablab.fr/Work/Neurospin/Data/sulcilab_test"

# # Chimps
# python cli/convert_mesh.py ${data_path}/chimps Elvira_New --sess 2020_shape_analysis_manual
# python cli/convert_mesh.py ${data_path}/chimps Kerri_New --sess 2020_shape_analysis_manual

# # Gorilla
# python cli/convert_mesh.py ${data_path}/gorilla Gorilla_Naku_Milwaukee --sess 2020_shape_analysis_manual

# # Humans
# python cli/convert_mesh.py ${data_path}/humans 009 --sess session1_manual
# python cli/convert_mesh.py ${data_path}/humans 014--sess session1_manual
# python cli/convert_mesh.py ${data_path}/humans 023 --sess session1_manual
# python cli/convert_mesh.py ${data_path}/humans 032 --sess session1_manual

# # Macaques
# python cli/convert_mesh.py ${data_path}/macaques ucdavis_032139 --sess default_session_KK
# python cli/convert_mesh.py ${data_path}/macaques ucdavis_032143 --sess default_session_KK

# Pongo
python cli/convert_mesh.py ${data_path}/pongo Pongo_Tupa_RLCorrect --sess 2020_shape_analysis_manual
