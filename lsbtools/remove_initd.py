# Begin /usr/lib/lsb/install_initd

import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

import argparse, glob, itertools, lsbtools, os, re
from io import StringIO


# Dictionary to map facilities to script names
facilities = {
  # special case for "$firs" and "$last" so that it's always first/last
  # This is exclusively for *dm scripts and reboot/halt
  "$last"      : "98",
  "$first"     : "01",
}

# Create map for headers index numbers used in "sysinit" and "matrix" lists
hindex = {
  "name"            : 0,
  "provides"        : 1,
  "required-start"  : 2,
  "required-stop"   : 3,
  "should-start"    : 4,
  "should-stop"     : 5,
  "start-runlevels" : 6,
  "stop-runlevels"  : 7,
}

# Find init.d directory
initdDir = lsbtools.find_initd_dir()

# Find rc base directory
rcdDir = lsbtools.find_rc_base_dir()

# Process command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Show verbose debug messages", action="store_true")
parser.add_argument("-d", "--dryrun", help="Show actions without modifying system", action="store_true")
parser.add_argument("--progver", help=argparse.SUPPRESS, action="store_true")
parser.add_argument("initfile", nargs="?", default="null", help="The init.d file to be deactivated")

args = parser.parse_args()

if args.progver:
  strver = lsbtools.get_prog_ver(sys.argv[0])
  print(strver, "\n")
  print("Copyright (C) 2020 DJ Lucas")
  print("This is free software; see the source for copying conditions.  There is NO")
  print("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
  print("\nWritten by DJ Lucas.\n")
  sys.exit(0)

if not os.path.exists(args.initfile):
  initfile = os.path.join(initdDir, args.initfile)
else:
  initfile = args.initfile
if not os.path.exists(initfile):
  print("Error! Initfile", initfile, "does not exist. Exiting...", file=sys.stderr)
  sys.exit(1)

if args.verbose:
  debug = 1
else:
  debug = 0

if args.dryrun:
  dryrun = 1
else:
  dryrun = 0

# Now, pull in all scripts and depdendencies in initdDir into lists
matrix = lsbtools.get_matrix(initdDir, debug)

# Update facilites -> script names
for s in matrix:
  for prov in s[hindex["provides"]]:
    if prov != s[hindex["name"]]:
      if debug == 1:
        print("Adding", prov, ":", s[hindex["name"]])
      facilities[prov] = s[hindex["name"]]

# Convert facilities that do not match script name to use script name
for s in matrix:
  for key in facilities.keys():
    for x in {hindex["provides"], hindex["required-start"], hindex["required-stop"], hindex["should-start"], hindex["should-stop"]}:
      for i in range(len(s[x])):
        s[x][i] = s[x][i].replace(key, facilities[key])

# Find what runlevels initfile is set to start and stop in
# First make sure it's installed adn then enabled
if not os.path.exists(initfile):
  print("Error!", initfile, "does not exist! Exiting...", file=sys.stderr)
  sys.exit(1)
  
# Find it in the matrix and see what runlevels it starts in
tindex = lsbtools.find_index(matrix, os.path.basename(initfile))
stlvls = matrix[tindex][hindex["start-runlevels"]]
splvls = matrix[tindex][hindex["stop-runlevels"]]

# Review all enabled scripts in those runlevels for Required-St{art,op} and
# report error and exit if any
stlist = []
splist = []
index = 0
while index < len(matrix):
  subindex = 0
  while subindex < len( matrix[index][hindex["required-start"]]):
    if matrix[index][hindex["required-start"]][subindex] == matrix[tindex][hindex["name"]]:
      # Only add to list if enabled
      link = "S??" + matrix[index][hindex["name"]]
      linkdir = "rc" + matrix[index][hindex["start-runlevels"]][0] + ".d"
      linkpath = os.path.join(rcdDir, linkdir, link)
      if glob.glob(linkpath):
        stlist.append(matrix[index][hindex["name"]])
    subindex += 1
  index += 1

index = 0
while index < len(matrix):
  subindex = 0
  while subindex < len( matrix[index][hindex["required-stop"]]):
    if matrix[index][hindex["required-stop"]][subindex] == matrix[tindex][hindex["name"]]:
      # Only add to list if enabled
      link = "K??" + matrix[index][hindex["name"]]
      linkdir = "rc" + matrix[index][hindex["stop-runlevels"]][0] + ".d"
      linkpath = os.path.join(rcdDir, linkdir, link)
      if glob.glob(linkpath):
        splist.append(matrix[index][hindex["name"]])
    subindex += 1
  index += 1

if len(stlist) > 0:
  printstr = os.path.basename(initfile) + ":"
  print("Requried-Start dependencies exist for", printstr, file=sys.stderr)
  for s in stlist:
    print(s)
  errorstr = os.path.basename(initfile) + "."
  print("Unable to remove", errorstr, "Exiting...", file=sys.stderr)
  sys.exit(1)

if len(splist) > 0:
  printstr = os.path.basename(initfile) + ":"
  print("Requried-Stop dependencies exist for", printstr, file=sys.stderr)
  for s in splist:
    print(s)
  errorstr = os.path.basename(initfile) + "."
  print("Unable to remove", errorstr, "Exiting...", file=sys.stderr)
  sys.exit(1)

# If no error so far, remove existing links (leave in initdDir)
for runlevel in matrix[tindex][hindex["start-runlevels"]]:
  link = "S??" + matrix[tindex][hindex["name"]]
  linkdir = "rc" + runlevel + ".d"
  linkpath = os.path.join(rcdDir, linkdir, link)
  if glob.glob(linkpath):
    if debug == 1 or dryrun == 1:
      print("Removing link:", glob.glob(linkpath)[0])
    if dryrun == 0:
      os.remove(glob.glob(linkpath)[0])
for runlevel in matrix[tindex][hindex["stop-runlevels"]]:
  link = "K??" + matrix[tindex][hindex["name"]]
  linkdir = "rc" + runlevel + ".d"
  linkpath = os.path.join(rcdDir, linkdir, link)
  if glob.glob(linkpath):
    if debug == 1 or dryrun == 1:
      print("Removing link:", glob.glob(linkpath)[0])
    if dryrun == 0:
      os.remove(glob.glob(linkpath)[0])

