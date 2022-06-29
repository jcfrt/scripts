#!/bin/env python3 
from pathlib import Path
import csv
from typing import Generator, Dict
import string
import re
import pprint
from sys import argv
from datetime import datetime


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


# Key to look for in the CSV file
SN_KEY = "Serial Number  (MDM page link)"
MDL_KEY = "Model (MDM)"
NAME_KEY = "Model Name (MDM)"

# NAME_RE = re.compile(r'.*\((.*)\)')
YEAR_NAME_RE = re.compile(r'.*,.*(20\d{2})')
SIZE_RE = re.compile(r'.*(\d{2}).inch')

class Tag():
  def __init__(self, row) -> None:
    self.sn = row.get(SN_KEY)
    self.model_name = row.get(MDL_KEY)
    self.name_mdm = row.get(NAME_KEY)

  @property
  def name(self) -> str:
    base = "DKU"

    # Remove lower case chars and ',' ie. "MacBookPro17,1" -> "MBP171"
    table = str.maketrans('', '', string.ascii_lowercase + ',')
    model = self.model_name.translate(table)

    name = self.name_mdm.split('(')
    name = name[1].strip(')')
    print(f"{self.sn} Name: {name}")
    arch = "M1"
    if not "M1" in name:
      arch = "X64"
    year = ""
    year_match = YEAR_NAME_RE.match(name)
    if year_match:
      year = year_match.group(1)
    size = ""
    size_match = SIZE_RE.match(name)
    if size_match:
      size = size_match.group(1)
    else:
      print("Screen size not found for {}: {}".format(self.sn, size))
  
    return f"{base}_{model}_{size}{arch}{year}_{self.sn}"

  def __repr__(self) -> str:
    return f"<{self.__class__.__name__}> {self.sn}"


if __name__ == "__main__":
  input_csv = Path(argv[1])
  sn_to_tags = {}
  for row in yield_from_CSV(input_csv):
    tag = Tag(row)
    sn = row.get(SN_KEY)
    if sn:
      sn_to_tags[sn] = tag.name

  pprint.pprint(sn_to_tags, indent=4, compact=False, width=400)

  today_date = datetime.today().strftime(r"%Y%m%d")
  with open(f'sn_to_tag_google_{today_date}.csv', 'w', newline='') as csvfile:
    fieldnames = ['Serial Number (mandatory)', 'Asset Tag']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')

    writer.writeheader()
    for sn, tag in sn_to_tags.items():
      writer.writerow(
        {
          fieldnames[0]: sn, 
          fieldnames[1]: tag
        }
      )