#!/usr/bin/env python3
# Begin lsbinitd.py

import glob, itertools, os, re, sys
from io import StringIO

# Treat LSB headers just like RFC 2822 (email headers)
# Derived from RFC822Parser from Debain initduitls.py
class ParseHeaders(dict):
  "A dictionary-like object."
  __linere = re.compile(r'([^:]+):\s*(.*)$')
  def __init__(self, fileob=None, strob=None, startcol=0, basedict=None):
    if fileob is None and strob is None:
      raise ValueError('need a file or string')
    if not basedict:
      basedict = {}
    super(ParseHeaders, self).__init__(basedict)
    if not fileob:
      fileob = StringIO(strob)
    key = None
    for line in fileob:
      if startcol:
        line = line[startcol:]
      if not line.strip():
        continue
      # Continuation line
      if line[0].isspace():
         if not key:
           continue
         self[key] += '\n' + line.strip()
         continue
      m = self.__linere.match(line)
      if not m:
        # Not a valid header
        continue
      key, value = m.groups()
      self[key] = value.strip()


beginre = re.compile(re.escape('### BEGIN INIT INFO'))
endre = re.compile(re.escape('### END INIT INFO'))

# Derrived from scan_intifile() from Debian initdutils.py
def scan_headers(initfile, debug):
  headerlines = ''
  scanning = False
  for line in open(initfile):
    line = line.rstrip()
    if beginre.match(line):
      scanning = True
      continue
    elif scanning and endre.match(line):
      scanning = False
      continue
    elif not scanning:
      continue
    if line.startswith('# '):
      headerlines += line[2:] + '\n'
    elif line.startswith('#\t'):
      headerlines += line[1:] + '\n'
  inheaders = ParseHeaders(strob=headerlines)
  headers = {}
  for header, body in inheaders.items():
    # Ignore empty headers
    if not body.strip():
      continue
    if header in ('Provides',
                  'Required-Start', 'Required-Stop',
                  'Should-Start', 'Should-Stop',
                  'Default-Start', 'Default-Stop'):
      headers[header] = body.split()
    else:
      headers[header] = body
  return headers


def find_index(listname, scriptname):
  index = 0
  if scriptname == "98":
    return (len(listname) - 1)
  if scriptname == "01":
    return 0
  while index < len(listname):
    if listname[index][0] == scriptname:
      return index
    index += 1
  # If we didn't find it, return a predictable number
  return 1000


def find_initd_dir():
  if os.path.exists("/etc/init.d"):
    if os.path.islink("/etc/init.d"):
      initdDir = os.path.realpath("/etc/init.d")
    else:
      initdDir = "/etc/init.d"
  elif os.path.exists("/etc/rc.d./init.d"):
    initdDir = "/etc/rc.d/init.d"
  else:
    print("Unable to locate init.d directory! Exiting...", file=sys.stderr)
    sys.exit(2)
  return initdDir


def find_rc_base_dir():
  if os.path.exists("/etc/rc.d"):
    if os.path.islink("/etc/rc.d"):
      rcdDir = os.path.realpath("/etc/rc.d")
    else:
      rcdDir = "/etc/rc.d"
  else:
    print("Unable to locate rc.d directory! Exiting...", file=sys.stderr)
    sys.exit(3)
  return rcdDir


def get_matrix(initdDir, debug):
  matrix = []
  for filename in os.listdir(initdDir):
    headers = scan_headers(os.path.join(initdDir, filename), debug)
    provides = headers.get('Provides', [])
    reqstart = headers.get('Required-Start', [])
    reqstop = headers.get('Required-Stop', [])
    shouldstart = headers.get('Should-Start', [])
    shouldstop = headers.get('Should-Stop', [])
    defstart = headers.get('Default-Start', [])
    defstop = headers.get('Default-Stop', [])
    if filename != "template" and filename != "rc":
      matrix.append([filename, provides, reqstart, reqstop, shouldstart, shouldstop, defstart, defstop,])
  return matrix
