#!/bin/bash 

# mv $DATA_ROOT/db.sqlite3 $DATA_ROOT/db.sqlite3.back;

python setup.py develop --user


# python manage.py migrate
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$SULCILAB_SUPERUSER_USERNAME', '$SULCILAB_SUPERUSER_EMAIL', '$SULCILAB_SUPERUSER_PASSWORD')" | python manage.py shell
# python manage.py setup_default_data
# python manage.py install_nomenclatures ./data/labels.csv /casa/host/src/brainvisa-share/master/nomenclature/hierarchy/sulcal_root_colors.hie
# python manage.py setup_demo_data ./.data

# Keycloak
# https://www.keycloak.org/getting-started/getting-started-docker
# sudo docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:18.0.2 start-dev
# Then go to: http://localhost:8080/admin/master/console

npm install
# npm i -D @nll/api-codegen-ts
# npm i -D rimraf
