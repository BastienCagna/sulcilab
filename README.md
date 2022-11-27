# SulciLab
SulciLab is a web based application for shared brain sulci labelling.


## Subprojects

### Sulcilab
The labelization database manager itself.

### Sulcilab GUI
A simple PyQT application to open Brainvisa labelization tools using th eSulcilab framework.

### Sulcilab Web
A ReactJS web frontend to connect to the Sulcilab database and labelize graphs online.


## Getting started
```shell
git clone https://github.com/BastienCagna/sulcilab_frontend.git
./setup.sh

# Start the backend
uvicorn sulcilab.main:app --reload

# Compile SCSS files (or use sass watcher in your IDE)
sass --watch sass:css

# Start the web frontend
npm run web-start
``` 

The React dev server use http://127.0.0.1:3000/

To build for production:
```shell
npm run build
```

## API 
To see the autogenerated docs: http://127.0.0.1:8000/docs#/
For now, the API URL must be hardcoded in the BASE property of OpenAPI in sulcilab_web/api/code/OpenAPI.ts.

### Build API client
Automatic generation of the typescript client:
```shell
npm run api-build
```


## Development


### Empty item
```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel


#############
# ORM Model #
#############


##################
# Pydantic Model #
##################


###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[P...])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, ..., skip=skip, limit=limit)

```


## Notes
### Expose dev server to network
sudo ufw allow 3000
npm run web-start --host 0.0.0.0

sudo ufw allow 5000
uvicorn sulcilab.main:app --reload --host 0.0.0.0 --port 5000

## Troubleshooting

If the watch fail limit is reached, before opening bv bash:
``̀ shell
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
