# Begin /usr/lib/lsb/install_initd

import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

import argparse, glob, itertools, lsbtools, os, re
from io import StringIO

# Dictionary to map facilities to script names
facilities = {
  # special case for "$first" and "$last" so that it's always first/last
  # This is exclusively for *dm scripts and reboot/halt
  "$first"    : "01",
  "$last"     : "98",
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
parser.add_argument("initfile", nargs="?", default="null", help="The new init.d file to be activated")

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

if args.verbose:
  debug = 1
else:
  debug = 0

if args.dryrun:
  dryrun = 1
else:
  dryrun = 0

if not os.path.exists(initfile):
  print("Error:", initfile, "does not exist! Exiting...", file=sys.stderr)
  print("Usage:",sys.argv[0], os.path.join(initdDir,"<init-script>"), "[-v|--verbose] [-h|--help", file=sys.stderr)
  sys.exit(1)

# Now, pull in all scripts and depdendencies in initdDir into lists
matrix = lsbtools.get_matrix(initdDir, debug)

# Update facilites -> script names
if debug == 1:
  print("Creating facilities array:")
  print("Adding $first : 01")
  print("Adding $last : 98")
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

# sysinit is a special case as it's independent of the others
sysinit = []
slist = []
for s in matrix:
  if len(s[hindex["start-runlevels"]]) > 0 and s[hindex["start-runlevels"]][0] == "S" or len(s[hindex["start-runlevels"]]) > 0 and s[hindex["start-runlevels"]][0] == "sysinit":
    strLink = 'S??' + s[hindex["name"]]
    fn = os.path.join(rcdDir, "rcS.d", strLink)
    if glob.glob(fn) or s[hindex["name"]] == os.path.basename(initfile):
      sysinit.append(s)
      slist.append(s[hindex["name"]])

# Create a dictionary for each runlevel that lists start scripts as well
# as a separate one that contains only the names (as was done for sysinit)
# Do start runlevels first

startlist = {}
startdict = {}
stoplist = {}
stopdict = {}

for runlevel in {0,1,2,3,4,5,6}:
  strll = []
  strld = []
  sprll = []
  sprld = []
  
  rcrldir = 'rc' + str(runlevel) + '.d'
  for s in itertools.chain(sysinit, matrix):
    for rl in s[hindex["start-runlevels"]]:
      if rl == str(runlevel):
        strLink = 'S??' + s[hindex["name"]]
        fn = os.path.join(rcdDir, rcrldir, strLink)
        if glob.glob(fn) or s[hindex["name"]] == os.path.basename(initfile):
          strll.append(s[hindex["name"]])
          strld.append(s)
    for rl in s[hindex["stop-runlevels"]]:
      if rl == str(runlevel):
        strLink = 'K??' + s[hindex["name"]]
        fn = os.path.join(rcdDir, rcrldir, strLink)
        if glob.glob(fn) or s[hindex["name"]] == os.path.basename(initfile):
          # Only if not already in sprll (could be in slist and appear twice)
          ct = 0
          for t in sprll:
            if s[hindex["name"]] == t:
              ct += 1
          if ct < 1:
            sprll.append(s[hindex["name"]])
            sprld.append(s)
  startlist[str(runlevel)] = strll
  startdict[str(runlevel)] = strld
  stoplist[str(runlevel)] = sprll
  stopdict[str(runlevel)] = sprld

# Order sysinit
maxiters = ( len(slist) * len(slist) )
loop = 0
iters = 0
nomoves = 0
if debug == 1:
  print("Organizing sysinit start scripts...")
while nomoves == 0:
  iters += 1
  if iters == maxiters:
    # We have a an endless loop
    loop = 1
  nomoves = 0
  index = 0
  moves = 0
  while index < len(slist):
    curindex = lsbtools.find_index(sysinit, slist[index])
    newindex = curindex
    indexsub = 0
    while indexsub < len(sysinit[curindex][hindex["required-start"]]):
      tempindex = lsbtools.find_index(sysinit, sysinit[curindex][hindex["required-start"]][indexsub])
      if tempindex == 1000:
        print("Error! Unable to locate Requried-Start dependency", sysinit[curindex][hindex["required-start"]][indexsub], "for script:", slist[index], file=sys.stderr)
        sys.exit(2)
      if tempindex > newindex:
        newindex = tempindex
      indexsub += 1
    indexsub = 0
    while indexsub < len(sysinit[curindex][hindex["should-start"]]):
      tempindex = lsbtools.find_index(sysinit, sysinit[curindex][hindex["should-start"]][indexsub])
      if tempindex != 1000 and tempindex > newindex:
        newindex = tempindex
      indexsub += 1
    if newindex != curindex:
      if loop == 1:
        # Wait to bail out here with a usable error message
        print("Reciprocal dependency detected between", startlist[str(runlevel)][index], "and",  startdict[str(runlevel)][newindex][hindex["name"]], "scripts!", file=sys.stderr)
        if debug == 0:
          print("Run with '-v' parameter to see the full list of afected scripts.\n", file=sys.stderr)
        else:
          print("", file=sys.stderr)
        sys.exit(3)
      # Remove it and then put it back in proper order
      if debug == 1:
        print("Moving", slist[index], "to after", sysinit[newindex][hindex["name"]])
      scriptvals = sysinit.pop(curindex)
      sysinit.insert(newindex, scriptvals)
      moves += 1
    index += 1
  if moves == 0:
    nomoves = 1

# Reorder start lists (only for RLs 1-5) exactly like above
for runlevel in {1,2,3,4,5}:
  maxiters = ( len(startlist[str(runlevel)]) * len(startlist[str(runlevel)]) )
  loop = 0
  iters = 0
  nomoves = 0
  if debug == 1:
    print("Organizing runlevel", str(runlevel), "start scripts...")
  while nomoves == 0:
    iters += 1
    if iters == maxiters:
      # We have a an endless loop
      loop = 1
    nomoves = 0
    index = 0
    moves = 0
    while index < len(startlist[str(runlevel)]):
      curindex = lsbtools.find_index(startdict[str(runlevel)], startlist[str(runlevel)][index])
      newindex = curindex
      indexsub = 0
      while indexsub < len(startdict[str(runlevel)][curindex][hindex["required-start"]]):
        tempindex = lsbtools.find_index(startdict[str(runlevel)], startdict[str(runlevel)][curindex][hindex["required-start"]][indexsub])
        if tempindex == 1000:
          # See if we are not in slist[]
          slerror = 1
          for sl in slist:
            if startdict[str(runlevel)][curindex][hindex["required-start"]][indexsub] == sl:
              # It's in sysinit, so just ignore it.
              slerror = 0
          if slerror == 1:
            print("Error! Unable to locate Requried-Start dependency", startdict[str(runlevel)][curindex][hindex["required-start"]][indexsub], "for script:", startlist[str(runlevel)][index], file=sys.stderr)
            sys.exit(2)
        if tempindex > newindex and tempindex != 1000:
          newindex = tempindex
        indexsub += 1
      indexsub = 0
      while indexsub < len(startdict[str(runlevel)][curindex][hindex["should-start"]]):
        tempindex = lsbtools.find_index(startdict[str(runlevel)], startdict[str(runlevel)][curindex][hindex["should-start"]][indexsub])
        if tempindex != 1000 and tempindex > newindex:
          newindex = tempindex
        indexsub += 1
      if newindex != curindex and newindex != 1000:
        if loop == 1:
          # Wait to bail out here with a usable error message
          print("Reciprocal dependency detected between", startlist[str(runlevel)][index], "and",  startdict[str(runlevel)][newindex][hindex["name"]], "scripts!", file=sys.stderr)
          if debug == 0:
            print("Run with '-v' parameter to see the full list of afected scripts.\n", file=sys.stderr)
          else:
            print("", file=sys.stderr)
          sys.exit(3)
        # Remove it and then put it back in proper order
        if debug == 1:
          print("Moving", startlist[str(runlevel)][index], "to after", startdict[str(runlevel)][newindex][hindex["name"]])
        scriptvals = startdict[str(runlevel)].pop(curindex)
        startdict[str(runlevel)].insert(newindex, scriptvals)
        moves += 1
      index += 1
    if moves == 0:
      nomoves = 1

# Stop scripts are reversed
for runlevel in {0,1,2,3,4,5,6}:
  nomoves = 0
  if debug == 1:
    print("Organizing runlevel", str(runlevel), "stop scripts...")
  while nomoves == 0:
    nomoves = 0
    index = 0
    moves = 0
    while index < len(stoplist[str(runlevel)]):
      curindex = lsbtools.find_index(stopdict[str(runlevel)], stoplist[str(runlevel)][index])
      newindex = curindex
      indexsub = 0
      while indexsub < len(stopdict[str(runlevel)][curindex][hindex["required-stop"]]):
        tempindex = lsbtools.find_index(stopdict[str(runlevel)], stopdict[str(runlevel)][curindex][hindex["required-stop"]][indexsub])
        if tempindex == 1000:
          # See if stop dep is started in sysinit
          slerror = 1
          #runlevels 1 and 2 are special cases WRT stop scripts
          if runlevel == 1 or runlevel == 2:
            prevlist = itertools.chain(slist, startlist[str(runlevel)])
          else:
            prevlist = slist
          for sl in prevlist:
            if stopdict[str(runlevel)][curindex][hindex["required-stop"]][indexsub] == sl:
              # It's in sysinit or started in current runnlevel, so just ignore
              slerror = 0
          if slerror == 1:
            print("Error! Unable to locate Requried-Stop dependency", stopdict[str(runlevel)][curindex][hindex["required-stop"]][indexsub], "for script:", stoplist[str(runlevel)][index], file=sys.stderr)
            sys.exit(2)
        if tempindex < newindex and tempindex != 1000:
          newindex = tempindex
        indexsub += 1
      indexsub = 0
      while indexsub < len(stopdict[str(runlevel)][curindex][hindex["should-stop"]]):
        tempindex = lsbtools.find_index(stopdict[str(runlevel)], stopdict[str(runlevel)][curindex][hindex["should-stop"]][indexsub])
        if tempindex != 1000 and tempindex < newindex:
          newindex = tempindex
        indexsub += 1
      if newindex != curindex and newindex != 1000:
        # Remove it and then put it back in proper order
        if debug == 1:
          print("Moving", stoplist[str(runlevel)][index], "to before", stopdict[str(runlevel)][newindex][hindex["name"]])
        scriptvals = stopdict[str(runlevel)].pop(curindex)
        stopdict[str(runlevel)].insert((newindex), scriptvals)
        moves += 1
      index += 1
    if moves == 0:
      nomoves = 1

# For scripts we manage, remove existing symlinks and create new for sysinit
rldir = os.path.join(rcdDir, "rcS.d")
for s in sysinit:
  sname = s[hindex["name"]]
  gname = "S??" + sname
  spath = os.path.join(rldir, gname)
  if glob.glob(spath):
    if debug == 1 or dryrun == 1:
      print("Removing", glob.glob(spath)[0])
    if dryrun == 0:
      os.remove(glob.glob(spath)[0])
if len(sysinit) > 0:
  increment = 100 // len(sysinit)
else:
  increment = 99
sid = 0
for s in sysinit:
  sname = s[hindex["name"]]
  target = os.path.join(rldir, sname)
  if sid < 10:
    strsid = "0" + str(sid)
  else:
    strsid = str(sid)
  gname = "S" + strsid + sname
  spath = os.path.join(os.path.relpath(initdDir, rldir), gname)
  if debug == 1 or dryrun == 1:
    print("Adding", spath, "->", target)
  if dryrun == 0:
    os.symlink(target, spath)
  sid += increment

# For the runlevels....
for runlevel in {0,1,2,3,4,5,6}:
  rltdir = "rc" + str(runlevel) + ".d"
  rldir = os.path.join(rcdDir, rltdir)
  for s in startdict[str(runlevel)]:
    sname = s[hindex["name"]]
    gname = "S??" + sname
    spath = os.path.join(rldir, gname)
    if glob.glob(spath):
      if debug == 1 or dryrun == 1:
        print("Removing", glob.glob(spath)[0])
      if dryrun == 0:
        os.remove(glob.glob(spath)[0])
  if len(startdict[str(runlevel)]) > 0:
    increment = 100 // len(startdict[str(runlevel)])
  else:
    increment = 99
  sid = 0
  for s in startdict[str(runlevel)]:
    sname = s[hindex["name"]]
    target = os.path.join(os.path.relpath(initdDir, rldir), sname)
    if sid < 10:
      strsid = "0" + str(sid)
    else:
      strsid = str(sid)
    gname = "S" + strsid + sname
    spath = os.path.join(rldir, gname)
    if debug == 1 or dryrun == 1:
      print("Adding", spath, "->", target)
    if dryrun == 0:
      os.symlink(target, spath)
    sid += increment
  for s in stopdict[str(runlevel)]:
    sname = s[hindex["name"]]
    gname = "K??" + sname
    spath = os.path.join(rldir, gname)
    if glob.glob(spath):
      if debug == 1 or dryrun == 1:
        print("Removing", glob.glob(spath)[0])
      if dryrun == 0:
        os.remove(glob.glob(spath)[0])
  if len(stopdict[str(runlevel)]) > 0:
    increment = 100 // len(stopdict[str(runlevel)])
  else:
    increment = 99
  sid = 0
  for s in stopdict[str(runlevel)]:
    sname = s[hindex["name"]]
    if sid < 10:
      strsid = "0" + str(sid)
    else:
      strsid = str(sid)
    gname = "K" + strsid + sname
    spath = os.path.join(rldir, gname)
    target = os.path.join(os.path.relpath(initdDir, rldir), sname)
    if debug == 1 or dryrun == 1:
      print("Adding", spath, "->", target)
    if dryrun == 0:
      os.symlink(target, spath)
    sid += increment

