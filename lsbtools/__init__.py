# Begin lsbtools/__init__.py

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
  elif os.path.exists("/etc/rc.d/init.d"):
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


def find_font_dir():
  lsb_fontdir = "/usr/share/fonts/lsb"
  if not os.path.exists(lsb_fontdir):
    os.mkdir(lsb_fontdir)
    os.chmod(lsb_fondir, 0o755)
  return lsb_fontdir


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

def get_prog_ver(strprogram):
  progver = strprogram + " " + " (LSB-Tools-0.9)"
  return progver

def install_font(argobject):
  fontDir = lsbtools.find_font_dir()
  aobject = os.path.basename(argsobject).strip(" ")
  fontfile = os.path.join(fontDir, aobject)
  if os.path.exists(fontfile):
    if check == 1:
      print(fontfile, "exists in filesystem.")
      sys.exit(0)
    elif remove == 1:
      os.remove(fontfile)
      print(fontfile, "successfully removed.")
      sys.exit(0)
    else:
      print("Error:", fontfile, "already exists in filesystem. Exiting...", file=sys.stderr)
      sys.exit(1)
  else:
    if check == 1:
      print(fontfile, "does not exist in filesystem.")
      sys.exit(1)
    elif remove == 1:
      print(fontfile, "does not exist in filesystem. No need to remove.")
      sys.exit(0)
    else:
      copyfile(argsobject, fontDir)
      os.chmod(fontfile, 0o644)
      sys.exit(0)

def install_init(argobject):
  initdDir = lsbtools.find_initd_dir()
  aobject = os.path.basename(argsobject).strip(" ")
  initfile = os.path.join(initdDir, aobject)
  if os.path.exists(initfile):
    if check == 1:
      print(initfile, "exists in filesystem.")
      sys.exit(0)
    elif remove == 1:
      os.remove(initfile)
      print(initfile, "successfully removed.")
      sys.exit(0)
    else:
      print("Error:", initfile, "already exists in filesystem. Exiting...", file=sys.stderr)
      sys.exit(1)
  else:
    if check == 1:
      print(initfile, "does not exist in filesystem.")
      sys.exit(1)
    elif remove == 1:
      print(initfile, "does not exist in filesystem. No need to remove.")
      sys.exit(0)
    else:
      copyfile(argsobject, initdDir)
      os.chmod(initfile, 0o644)
      sys.exit(0)

def install_profile(argobject):
  profileDir = "/etc/profile.d"
  aobject = os.path.basename(argsobject).strip(" ")
  profilefile = os.path.join(profileDir, aobject)
  if os.path.exists(profilefile):
    if check == 1:
      print(profilefile, "exists in filesystem.")
      sys.exit(0)
    elif remove == 1:
      os.remove(profilefile)
      print(initfile, "successfully removed.")
      sys.exit(0)
    else:
      print("Error:", profilefile, "already exists in filesystem. Exiting...", file=sys.stderr)
      sys.exit(1)
  else:
    if check == 1:
      print(profilefile, "does not exist in filesystem.")
      sys.exit(1)
    elif remove == 1:
      print(profilefile, "does not exist in filesystem. No need to remove.")
      sys.exit(0)
    else:
      copyfile(argsobject, profileDir)
      os.chmod(profilefile, 0o644)
      sys.exit(0)

def install_service(argobject):
  portproto = argobject[0].split("/")
  if len(portproto) != 2:
    print("Invalid syntax! The first argument of type service must be in port/proto\nformat, followed by service name and any aliases. Ex: 80/tcp http webserver")
  portservice = argobject[1]
  if len(argobject) > 2:
    servalias = ''
    count=2
    while count < len(argobject):
      servalias = servalias + argobject[count] + ' '
      count += 1
  if check == 1:
    try:
      portcheck = socket.getservbyname(portservice, portproto[1])
    except OSError:
      portcheck = 'error'
    try:
      namecheck = socket.getservbyport(int(portproto[0]), portproto[1])
    except OSError:
      namecheck = 'error'
    if portcheck == portproto[0] and namecheck == portservice:
      print("Service", portservice, "with port", portproto[0], "on protocol", portproto[1], "exists.")
      sys.exit(0)
  if remove == 1:
    print("Service removal is not currently supported. Exiting...", file=sys.stderr)
    sys.exit(1)

  if servalias == '':
    print("Adding service", portservice, "with port", portproto[0], "on protocol", portproto[1])
  else:
    print("Adding service", portservice, "with port", portproto[0], "on protocol", portproto[1], "with aliases:", servalias)
  try:
    nameservice = socket.getservbyport(int(portproto[0]), portproto[1])
  except OSError:
    nameservice = 'error'
  if portservice != nameservice:
    namesp = 25 - len(portservice) - len(argobject[0])
    fmtstr = portservice
    count = 0
    while count < namesp:
      fmtstr = fmtstr + ' '
      count += 1
    fmtstr = fmtstr + argobject[0]
    servicesfile=open("/etc/services", "a")
    servicesfile.write("%s\r\n", fmtstr)
    servicesfile.close()
    sys.exit(0)
  else:
    print("Service", portservice, "with port", portproto[0], "on protocol", portproto[1], "exists.")
    sys.exit(0)

def install_inet(argsobject):
  print("Not implemented...")
  sys.exit(0)

def install_crontab(argsobject):
  print("Not implemented...")
  sys.exit(0)

def install_package(argsobject):
  print("Not implemented...")
  sys.exit(0)

def install_menu(argsobject):
  print("Not implemente...")
  sys.exit(0)

def install_ldconfig(argsobject):
  print("Not implemente...")
  sys.exit(0)

def install_man(argsobject):
  print("Not implemente...")
  sys.exit(0)

