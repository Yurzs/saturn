import datetime

version = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y.%m.%d.%H%M')

try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''


with open('setup.txt', 'r') as text:
    with open('setup.py', 'w') as setup:
        txt = text.read()
        setup.write(txt.format(version=version, long_description=long_description))