#!/bin/bash -e

# Automate removal of Tenable's Nessus agent (used during the cyber security audits)
# This script needs to run with admin privileges.

NESSUS_PARENT_PATH="/Library/NessusAgent"
NESSUS_CLI="${NESSUS_PARENT_PATH}/run/sbin/nessuscli"

# Test if the Nessus agent has not already been removed from the machine:
if [ ! -f "${NESSUS_CLI}" ]; then
  echo "No application found in ${NESSUS_CLI}. Exiting."
  exit 0
fi
echo "Nessus application found in ${NESSUS_CLI}"

echo "Unlinking the Nessus agent from the server..." 
"${NESSUS_CLI}" agent unlink --force || echo "Agent failed to unlink properly. Continuing removal..."

echo "Removing the Nessus application from disk..."
[ ! -d "${NESSUS_PARENT_PATH}" ] || echo "${NESSUS_PARENT_PATH} did not exist, continuing anyway..."

rm -rf "${NESSUS_PARENT_PATH}"
rm -f '/Library/LaunchDaemons/com.tenablesecurity.nessusagent.plist'
rm -rf '/Library/PreferencePanes/Nessus Agent Preferences.prefPane'

echo "Disabling the nessus Agent service..."
launchctl remove com.tenablesecurity.nessusagent || :

echo "Successfully removed Nessus from this device."
