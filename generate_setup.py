from saturn.version import __version__
import os


with open("./saturn/version", "w") as ver_file:
    if "MAJOR" in os.environ.get("CI_COMMIT_DESCRIPTION", ""):
        major_version = int(__version__.split()[0]) + 1
        minor_version = 0
    else:
        major_version = int(__version__.split()[0])
        minor_version = int(__version__.split()[1]) + 1
    full_version = f"{major_version}.{minor_version}"
    ver_file.write(f"__version__ = \"{full_version}\"")

try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""


with open("setup.txt", "r") as text:
    with open("setup.py", "w") as setup:
        txt = text.read()
        setup.write(txt.format(version=full_version, long_description=long_description))