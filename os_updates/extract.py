#!/bin/env python3
import csv
from typing import Generator, Dict, Union, List
from pathlib import Path
from sys import argv
from collections import defaultdict
from packaging import version
import json
import pprint
import logging
log = logging.getLogger()
logging.basicConfig()
log.setLevel(logging.DEBUG)

# From a TSV file exported from google admin logs with the following headers:
# Device Name,Name,Email,Ownership,Type,Model,First Sync,Last Sync,Status,Device ID,Serial Number (mandatory),IMEI / MEID,OS,User Agent,Host Name
# the output should be a mapping where keys are the Email field values (therefore unique),
# and values for each should be a list (or mapping) of any obsolete OS version
# per device type.
# A second output should be a csv representing each email (user) and the custom
# text to send them by email. 
# Example: "iOS, Mac devices" for "please update your iOS, Mac devices ASAP"


def yield_from_CSV(csv_file_path: Path, delimiter='\t') -> Generator[Dict[str, str], None, None]:
  """
  Yield each line from a CSV file as a mapping of strings
  """
  with open(csv_file_path, 'r') as f:
    csv_reader = csv.DictReader(f, delimiter=delimiter)
    if not csv_reader:
      raise Exception(f"No data found in input file {csv_file_path.name}.")
    
    for row in csv_reader:
      yield row


MACOS_MIN_VERSION = version.parse("10.15.7") # (Catalina)
WINDOWS_MIN_VERSION = version.parse("10.0.19044.1767") # (Version 21H2)
IOS_MIN_VERSION = version.parse("15.5")
ANDROID_MIN_VERSION = version.parse("10.0.0") # "10.0.0_r67"
LINUX_MIN_VERSION = version.parse("5.7")


def is_obsolete_version(version_str: str) -> bool:
  version_str = version_str.strip()
  vnum = version_str.split(" ")
  if len(vnum):
    vnum = vnum[-1]
  parsed_vnum = version.parse(vnum)
  if "android" in version_str.lower() and parsed_vnum < ANDROID_MIN_VERSION:
      return "Android device"
  if "ios" in version_str.lower() and parsed_vnum < IOS_MIN_VERSION:
    return True
  if "macos" in version_str.lower() and parsed_vnum < MACOS_MIN_VERSION:
    return True
  if "windows" in version_str.lower() and parsed_vnum < WINDOWS_MIN_VERSION:
    return True
  return False


if __name__ == "__main__":
  # Grab offboarded users if we have one
  offboarded_user_emails = set()
  offboarded_csv = Path("offboarded_users_gam.csv")
  if offboarded_csv.exists():
    for row in yield_from_CSV(offboarded_csv):
      if email := row.get("primaryEmail"):
        offboarded_user_emails.add(email)
  log.info(f"Got {len(offboarded_user_emails)} offboarded users that we will ignore.")

  # Need users who are in the /protected OU as well, so dead code for now:
  # active_user_emails = set()
  # onboarded_csv = Path("User_Download_28062022_105716.csv") # active_users.csv
  # if onboarded_csv.exists():
  #   for row in yield_from_CSV(onboarded_csv, delimiter=','):
  #     if email := row.get("Email Address [Required]"):
  #       active_user_emails.add(email)
  #   print(f"Got {len(active_user_emails)} active users from Google directory.")

  generate_simple_message = False

  # Merge two different CSV exports (ie. Windows and Mac) into one 
  # if more than one dataset passed as arguments
  merged_dataset = [] # list of rows
  for arg in argv[1:]:
    input_csv = Path(arg)
    log.info(f"Loading input file: {input_csv}")
    if not input_csv.exists():
      print(f"File {input_csv.name} does not exist. Exiting.")
      exit(1)
    for row in yield_from_CSV(input_csv, delimiter=','):
      merged_dataset.append(row)

  # pprint.pprint(merged_dataset, indent=4)

  skipped = set()
  user_map = defaultdict(lambda: {"devices": {}, "name": ""})
  for row in merged_dataset:  
    email = row.get("Email")
    device_type = row.get("Type")
    
    if not email or not device_type:
      skipped.add(email)
      log.debug(
        f"Skipping row due to missing email or device type. "
        f"Email: {row.get('Email')}, Type: {row.get('Type')}.\n"
        f"row {row}")
      continue
    
    if email in offboarded_user_emails: # or email not in active_user_emails:
      skipped.add(email)
      log.info(f"Skipping already offboarded user: {email}")
    
    _version = row.get("OS")
    # print(f"{email}: OS: {_version}")
    
    if is_obsolete_version(_version):
      log.debug(f"{_version} for {email} is obsolete.")
      if prev_version := user_map.get(email, {}).get("devices", {}).get(device_type, None):
        if version.parse(prev_version) > version.parse(_version):
          log.debug(
            f"Skiping {device_type} version {_version} due to an already "
            f"recorded version {prev_version}"
          )
          continue
      user_map[email]["devices"][device_type] = _version
      user_map[email]["name"] = row.get("Name")

  print(f"Filtered out {len(skipped)} users who have been offboarded already.")

  # print(json.dumps(user_map, indent=2, ensure_ascii=False))

  print(f"{len(user_map)} users with non-compliant OS versions.")
  
  with open("emails_to_found_obsolete_os.json", 'w') as f:
    json.dump(user_map, f, indent=2, ensure_ascii=False)

  # Recreate values with ones that will be directly replaced in warning email template
  user_to_message = defaultdict(lambda: {})
  for email, data in user_map.items():
    # Generate a string like "Mac, iOS, Windows devices"
    if generate_simple_message:
      for dev in data.get("devices"):
        user_to_message[email]["message"] = ", ".join([d for d in data["devices"].keys()]) + " device"
      if len(data.get("devices")) > 1:
        # add plural mark
        user_to_message[email]["message"] += "s"

    # Simply list os version (useful if we have an import CSV for only Mac, or only Windows)
    for dev in data.get("devices"):
      # We should only have one device in this case
      user_to_message[email]["message"] = list(data.get("devices", {}).values())[0]

    # Add the name of the user, for better greeting at the beginning of the email
    user_to_message[email]["name"] = data.get("name")


  # export to CSV in order to load in Google Sheets
  with open('emails_to_devices_to_update.csv', 'w', newline='') as csvfile:
    fieldnames = ['Email', 'Name', 'Devices to update']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()
    for email, data in user_to_message.items():
      writer.writerow(
        {
          fieldnames[0]: email, 
          fieldnames[1]: data.get("name"), 
          fieldnames[2]: data.get("message")
        }
      )