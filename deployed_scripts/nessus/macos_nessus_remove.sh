#!/bin/zsh

# Automate removal of Tenable's Nessus agent (used during the cyber security audits)
# This script need to run with admin privileges.

NESSUS_PARENT_PATH="/Library/NessusAgent"
NESSUS_CLI="${NESSUS_PARENT_PATH}/run/sbin/nessuscli"

# Test if the Nessus agent has not already been removed from the machine:
if [ ! -f ${NESSUS_CLI} ]; then
  echo "No application found in ${NESSUS_CLI}. Exiting."
  exit 0
fi
echo "Nessus application found in ${NESSUS_CLI}"

echo "Unlinking the Nessus agent from the server..." 
${NESSUS_CLI} agent unlink --force

echo "Removing the Nessus application from disk..."
rm -rf "${NESSUS_PARENT_PATH}"
rm '/Library/LaunchDaemons/com.tenablesecurity.nessusagent.plist'
rm -r '/Library/PreferencePanes/Nessus Agent Preferences.prefPane'

echo "Disabling the nessus Agent service..."
echo launchctl remove com.tenablesecurity.nessusagent

echo "Successfully removed Nessus from this device."