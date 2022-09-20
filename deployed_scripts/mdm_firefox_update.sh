#!/bin/zsh
# This script installs/updates the latest version of the Firefox web browser for MacOS

URL='https://download.mozilla.org/?product=firefox-latest&os=osx&lang=en-US'
OUT_DIR="/tmp"
APP_NAME="Firefox"
OUT_FILENAME="$APP_NAME.dmg"
OUT_PATH="$OUT_DIR/$OUT_FILENAME"
APP_DIR="$APP_NAME.app"
INSTALLATION_PATH="/Applications"
MOUNT_BASE="/Volumes/$APP_NAME"
MOUNT_PATH="$MOUNT_BASE/$APP_DIR"
INSTALLED_APP_PATH="$INSTALLATION_PATH/$APP_DIR"

# check existence
if [ ! -d "$INSTALLED_APP_PATH" ];
    then
        echo "$INSTALLED_APP_PATH does not exist, $APP_NAME is probably not installed. Exiting."
    exit 0
fi

# clean old
echo "Removing previously downloaded $OUT_FILENAME" && rm -f "$OUT_PATH";

# Downloading archive
echo "Downloading $APP_NAME..."
curl -L -s -o $OUT_FILENAME --output-dir $OUT_DIR $URL --
echo "Downloaded file $OUT_FILENAME to $OUT_PATH.";

# mount archive
hdiutil attach -quiet $OUT_PATH

# copy binary
rsync -rtvpl $MOUNT_PATH $INSTALLATION_PATH

# fix binary attributes
xattr -cr $INSTALLED_APP_PATH

#umount image
hdiutil detach $MOUNT_BASE

# clean archive
rm $OUT_PATH;
