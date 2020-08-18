#!/usr/bin/python3.7
# Begin /usr/bin/lsb_release

import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

import argparse, glob, itertools, lsbtools, os, re

# Set default values
config = {
  'LSB_VERSION'         : 'unavailable',
  'DISTRIB_ID'          : 'unavailable',
  'DISTRIB_DESCRIPTION' : 'unavailable',
  'DISTRIB_RELEASE'     : 'unavailable',
  'DISTRIB_CODENAME'    : 'unavailable',
}
printval = ''

# Process command line argurments
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="Display the version of the LSB specification against which the distribution is compliant", action="store_true")
parser.add_argument("-i", "--id", help="Display the string id of the distributor", action="store_true")
parser.add_argument("-d", "--description", help="Display the single line text description of the distribution", action="store_true")
parser.add_argument("-r", "--release", help="Display the release number of the distribution", action="store_true")
parser.add_argument("-c", "--codename", help="Display the codename according to the distribution release", action="store_true")
parser.add_argument("-a", "--all", help="Display all of the above information", action="store_true")
parser.add_argument("-s", "--short", help="Display all of the above information in short output format", action="store_true")
parser.add_argument("--progver", help=argparse.SUPPRESS, action="store_true")
args = parser.parse_args()

if args.progver:
  strver = lsbtools.get_prog_ver(sys.argv[0])
  print(strver, "\n")
  print("Copyright (C) 2020 DJ Lucas")
  print("This is free software; see the source for copying conditions.  There is NO")
  print("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
  print("\nWritten by DJ Lucas.\n")
  sys.exit(0)


if args.version:
  lv = 1
else:
  lv = 0

if args.id:
  li = 1
else:
  li =0

if args.description:
  ld = 1
else:
  ld = 0

if args.release:
  lr = 1
else:
  lr = 0

if args.codename:
  lc = 1
else:
  lc = 0

if args.all:
  lv = 1
  li = 1
  ld = 1
  lr = 1
  lc = 1

if args.short:
  ls = 1
else:
  ls = 0

if lv == 0 and li == 0 and ld == 0 and lr == 0 and lc == 0:
  lv = 1

# Read required configuration file
if not os.path.exists("/etc/lsb-release"):
  print("Required configuration file '/etc/lsb-relase' is not found. Exiting...", file=sys.stderr)
  sys.exit(1)

conffile = open("/etc/lsb-release", 'r')
content = conffile.read()
items = content.split('\n')
for pair in items:
  if pair != '':
    key,val = pair.split('=')
    config[key] = val.strip('\"')
conffile.close()

# As of LSB-2.0, the LSB Version string is comprised of colon separated modules
# A module can be represented directly in the LSB_VERSION value or consist
# of empty files with the name of the module in /etc/lsb-release.d/
lsbver = ''
if not os.path.isdir("/etc/lsb-release.d"):
  lsbver = config['LSB_VERSION']
else:
  if len(os.listdir('/etc/lsb-release.d')) == 0:
    lsbver = config['LSB_VERSION']
  else:
    if config['LSB_VERSION'] != 'unavailable':
      lsbver = config['LSB_VERSION']
    # See what else is there
    for lsbfile in os.listdir('/etc/lsb-release.d'):
      if lsbver == '':
        lsbver = basename(lsbfile)
      else:
        lsbver = lsbver + ":" + lsbfile

# Set the LSB Version to our assembled string
config['LSB_VERSION'] = lsbver.strip(' ')

if lv == 1:
  if ls == 1:
    printval = printval + " " + config['LSB_VERSION']
  else:
    lprintval = "LSB Version:\t" + config['LSB_VERSION']
    print(lprintval)

if li == 1:
  if ls == 1:
    printval = printval + " " + config['DISTRIB_ID']
  else:
    lprintval = "Distributor ID:\t" + config['DISTRIB_ID']
    print(lprintval)

if ld == 1:
  if ls == 1:
    printval = printval + " " + config['DISTRIB_DESCRIPTION']
  else:
    lprintval = "Description:\t" + config['DISTRIB_DESCRIPTION']
    print(lprintval)

if lr == 1:
  if ls == 1:
    printval = printval + " " + config['DISTRIB_RELEASE']
  else:
    lprintval = "Release:\t" + config['DISTRIB_RELEASE']
    print(lprintval)

if lc == 1:
  if ls == 1:
    printval = printval + " " + config['DISTRIB_CODENAME']
  else:
    lprintval = "Codename:\t" + config['DISTRIB_CODENAME']
    print(lprintval)

if ls == 1:
  print(printval.strip(" "))

