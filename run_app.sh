#!/usr/bin/env bash
export FLASK_APP=application.py
export DATABASE_URL=postgres://twzehpfjmjpwbi:2acd1a06932ba16abcd87c30a850df85fcb254c077d824159968983b2bec0e9d@ec2-50-19-222-129.compute-1.amazonaws.com:5432/depr2vhd2q1rfj
flask run --port $PORT
