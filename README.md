# nmapscan project
## requirement
python 3.5+

## install
```
pip3 install -r requirements.txt
```
modify settings.py

## run
```
celery -A nmapscan worker -l info -B
```