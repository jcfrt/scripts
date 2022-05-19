#!/bin/zsh
############
# This script installs/updates the latest version of the Firefox web browser.
############
# 1.1 - Sandray Douglas / Jean-Carol Forato - 19-06-2022
#        * Use shell before calling the python interpreter.
# 1.0 - Sandray Douglas - 19-06-2022
#        * Initial script creation.
############

PYTHON="python3"
PYTHON="$(command -v "python3")"
FOUND=$?

if ! PYTHON_LOC="$(command -v "$PYTHON")" || [[ -z $PYTHON_LOC ]]; then
    echo "Looking for python2..."
    PYTHON="python"
    if ! PYTHON_LOC="$(command -v "$PYTHON")" || [[ -z $PYTHON_LOC ]]; then
        echo "python could not be found on this machine! Aborting."; 
        exit 1;
    fi
fi

echo "Found python interpreter at ${PYTHON_LOC}"

${PYTHON_LOC} - << END
import os
from distutils.dir_util import copy_tree
from pathlib import Path

url = "https://download.mozilla.org/?product=firefox-nightly-latest-l10n-ssl&os=osx&lang=en-GB"
# server='https://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US'
output_dir = Path("/tmp/")
# output_file = "firefox-102.0a1.en-GB.mac.dmg"
output_base_filename = "Firefox.dmg"
old_installer_path = output_dir / output_base_filename

if old_installer_path.exists():
    old_installer_path.unlink()
    
installed_app = Path("/Applications/Firefox.app")

cmd = 'curl -L -o Firefox.dmg --output-dir \"{}\" {}'.format(str(output_dir), url)
os.system(cmd)

print("Firefox.dmg downloaded")

exit(5)

if installed_app.exists():
    cmd = 'hdiutil attach -nobrowse -mountpoint "/Volumes/Firefox" "/tmp/Firefox.dmg"'
    os.system(cmd)
    copy_tree("/Volumes/Firefox/Firefox.app", "/Applications/Firefox.app")
    cmd = 'hdiutil detach "/Volumes/Firefox"'
    os.system(cmd)
    cmd = 'rm /tmp/Firefox.dmg'
    os.system(cmd)
else:
    cmd = 'hdiutil attach -nobrowse -mountpoint "/Volumes/Firefox" "/tmp/Firefox.dmg"'
    os.system(cmd)
    cmd = 'cp -R /Volumes/Firefox/Firefox.app /Applications/Firefox.app '
    os.system(cmd)
    cmd = 'hdiutil detach "/Volumes/Firefox"'
    os.system(cmd)
    cmd = 'rm /tmp/Firefox.dmg'
    os.system(cmd)
END