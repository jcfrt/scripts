#!/bin/zsh
############
# This script installs/updates the latest version of the Firefox web browser.
############
# 1.3 - Sandray Douglas / Jean-Carol Forato - 20-06-2022
#        * Script not truly functional yet, install seems corrupted.
# 1.2 - Sandray Douglas / Jean-Carol Forato - 19-06-2022
#        * Use shell script instead.
# 1.1 - Sandray Douglas / Jean-Carol Forato - 19-06-2022
#        * Use shell before calling the python interpreter.
# 1.0 - Sandray Douglas - 19-06-2022
#        * Initial script creation.
############

# TODO use the $LANG env variable to fetch the proper language version
URL='https://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US'
# DEBUGGING URL
# URL='https://download.mozilla.org/?product=firefox-nightly-latest-l10n-ssl&os=osx&lang=en-GB'
OUT_DIR="/tmp"
APP_NAME="Firefox"
# DEBUGGING APP name
# APP_NAME="Firefox Nightly"
OUT_FILENAME="$APP_NAME.dmg"
OUT_PATH="$OUT_DIR/$OUT_FILENAME"

[ -f "$OUT_PATH" ] && echo "Removing previously downloaded $OUT_FILENAME" && rm "$OUT_PATH"

echo "Downloading $APP_NAME..."
curl -s -L -o $OUT_FILENAME --output-dir $OUT_DIR $URL --

echo "Downloaded file $OUT_FILENAME to $OUT_PATH."

APP_DIR="$APP_NAME.app"
INSTALLATION_PATH="/Applications"
MOUNT_BASE="/Volumes/$APP_NAME"
MOUNT_PATH="$MOUNT_BASE/$APP_DIR"
INSTALLED_APP_PATH="$INSTALLATION_PATH/$APP_DIR"

[ ! -d "$INSTALLED_APP_PATH" ] \
&& echo "$INSTALLED_APP_PATH does not exist, $APP_NAME is probably not installed. Exiting." \
&& exit 2

OUTPUT=$(hdiutil attach -nobrowse "$OUT_PATH")
[ $? -eq 0 ] || exit 3

MOUNTED="$(echo $OUTPUT | grep -i $APP_NAME | awk -F'\t' '{print $3}')";
[ $? -ne 0 ] && echo "Failed to mount at $MOUNTED" && exit 4
echo "Mounted installation dmg at $MOUNTED."

# FIXME after forcing the installation (below), Firefox fails to start and MacOS
# detects it as being corrupted. Removing /Applications/Firefox.app and reinstalling
# fixes the issue, but this should not be happening in the first place.

# Force update the binaries by copying files from the installer (dmg) file
cp -apRf "$MOUNT_PATH/" "$INSTALLED_APP_PATH"

# User should be part of the admin group already
# chown -R :admin "$INSTALLED_APP_PATH";
# Allow the user to modify the files (for automatic updates)
# chmod -R g+w "$INSTALLED_APP_PATH";

[ $? -ne 0 ] && echo "Failed to copy new version to $INSTALLED_APP_PATH" && exit 5

hdiutil detach "$MOUNTED"
rm $OUT_PATH