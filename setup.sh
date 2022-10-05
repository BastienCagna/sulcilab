#!/bin/bash

# mv $DATA_ROOT/db.sqlite3 $DATA_ROOT/db.sqlite3.back;

if which node > /dev/null
then
    echo "node is installed, skipping..."
else
    # add deb.nodesource repo commands 
    # install node
    echo "install node"
    ./install_node.sh
fi


python setup.py develop --user
npm install

# mv db.sqlite db.sqlite.back

python cli/create_account.py admin Admin admin --admin
python cli/setup_default_data.py
python cli/install_nomenclatures.py ./data/labels.csv ./data/sulcal_root_colors.hie

# python manage.py migrate
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$SULCILAB_SUPERUSER_USERNAME', '$SULCILAB_SUPERUSER_EMAIL', '$SULCILAB_SUPERUSER_PASSWORD')" | python manage.py shell
# python manage.py setup_default_data
# python manage.py install_nomenclatures ./data/labels.csv /casa/host/src/brainvisa-share/master/nomenclature/hierarchy/sulcal_root_colors.hie
# python manage.py setup_demo_data ./.data

# Keycloak
# https://www.keycloak.org/getting-started/getting-started-docker
# sudo docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:18.0.2 start-dev
# Then go to: http://localhost:8080/admin/master/console
