#!/bin/bash
source ./venv/bin/activate
cd ${PWD}/src/app
flask run --host 0.0.0.0
