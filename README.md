# SulciLab Backend
SulciLab is a web based application for shared brain sulci labelling.

## Getting started

### Requirements
Python >= 3.10
```
python3
python3-venv
```

### Setup
```shell
git clone https://github.com/BastienCagna/sulcilab_frontend.git
python3 -m venv venv
. venv/bin/activate
./setup.sh
cd sulcilab
uvicorn main:app --reload
``` 

