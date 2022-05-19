#!/usr/bin/python
############
# This script installs/updates the latest ESR version of the Firefox web browser.
############
# 1.0 - Jorge Escala - 2014-12-24
#        * Initial script creation.
############

import re, os
from distutils.dir_util import copy_tree
from os.path import isfile
from plistlib import readPlist
from ftplib import FTP

server='ftp.mozilla.org'
path='pub/mozilla.org/firefox/releases/latest-esr/mac/en-US'
plistFile='/Applications/Firefox.app/Contents/Info.plist'
DEBUG=False

ftp=FTP(server)
ftp.login()
ftp.cwd(path)
fileList=(ftp.nlst())

# Get latest version of Firefox and filename
latestFirefoxDownload=next(i for i in fileList if re.match( r'Firefox.*.dmg', i))
latestFirefoxVersion=latestFirefoxDownload[8:-7]

# Get currently installed version of Firefox
if isfile(plistFile):
    pl = readPlist(plistFile)
    currentFirefoxVersion=pl["CFBundleShortVersionString"]
else:
    currentFirefoxVersion="none"

if DEBUG:
    print("current: "+currentFirefoxVersion)
    print("latest: "+latestFirefoxVersion)

if latestFirefoxVersion != currentFirefoxVersion:
    ftp.retrbinary('RETR '+latestFirefoxDownload, open('/tmp/Firefox.dmg', 'wb').write)
    commandCall='hdiutil attach -nobrowse -mountpoint "/Volumes/Firefox" "/tmp/Firefox.dmg"'
    os.system(commandCall)
    copy_tree("/Volumes/Firefox/Firefox.app", "/Applications/Firefox.app")
    commandCall='hdiutil detach "/Volumes/Firefox"'
    os.system(commandCall)
