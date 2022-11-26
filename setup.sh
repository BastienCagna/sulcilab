#!/bin/bash

# if which node > /dev/null
# then
#     echo "node is installed, skipping..."
# else
#     # add deb.nodesource repo commands 
#     # install node
#     echo "install node"
#     ./install_node.sh
# fi

# # python -m venv venv
# # . venv/bin/activate

# python setup.py develop --user
# npm install

mv db.sqlite db.sqlite.back
# cp db.sqlite.back db.sqlite

python cli/create_account.py admin admin admin --admin
python cli/setup_default_data.py
python cli/install_nomenclatures.py ./data/labels.csv ./data/sulcal_root_colors.hie

# BUILD the FastAPI javascript client
npm run api-build

# Setup at Neurospin
# python cli/import_db.py /neurospin/dico/data/bv_databases/human/manually_labeled/archi Archi archi 3.3 session1_manual Human
