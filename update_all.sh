#!/bin/bash
python update_dicts.py
echo 'Going to upload the changes on Google app server now.'
python ../appcfg.py update app.yaml