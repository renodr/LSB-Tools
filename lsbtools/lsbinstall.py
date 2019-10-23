# Begin /usr/bin/lsbinstall

import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

import argparse, glob, itertools, lsbtools, os, re, socket, textwrap
from shutil import copyfile

def inst_inet(argobject):
  lsbtools.read_inet(argobject)
  lsbtools.install_inet(argobject)

def inst_crontab(argobject):
  lsbtools.read_crontab(argobject)
  lsbtools.install_crontab(argobject)

def inst_package(argobject):
  lsbtools.read_package(argobject)
  lsbtools.install_package(argobject)

def inst_menu(argobject):
  lsbtools.read_menu(argobject)
  lsbtools.isntall_menu(argobject)

def inst_ldconfig(argobject):
  lsbtools.read_ldconfig(argobject)
  lsbtools.install_ldconfig(argobject)

def inst_man(argobject):
  lsbtools.read_man(argobject)
  lsbtools.install_man(argobject)

# Process command line argurments
parser = argparse.ArgumentParser(
      description="installation tool for various types of data",
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog=textwrap.dedent("""\
         object types:
           font           Install a font into the systemwide font repository
           init           Install an init script into the system repository
           profile        Install a profile script into the system repository
           service        Ensure a service name, number proto pair is known to
                          the system service database
                          Services are represetned as:
                              port/proto name [alias1...]
           inet           Add an entry to the systems network super daemon
                          configuration
                          inet service files will have the format:
                              service <service_name>
                              {
                                      <attribute> <assign-op> <value ...>
                              }
           crontab        Install a job into the system crontab
           package        Install an LSB compliant RPM package
           menu           Install a desktop menu entry into the system menu
           ldconfig       Register a directory that contains shared libraries
           man            Install a manual page into the system manual repository
      """))
parser.add_argument("-c", "--check", action="store_true")
parser.add_argument("-r", "--remove", action="store_true")
parser.add_argument("-t", "--type", required=True, action="store")
parser.add_argument("object", nargs='+', action="store")
args = parser.parse_args()

# Avoid extraneous use of not
if args.check:
  check = 1
else:
  check = 0

if args.remove:
  remove = 1
else:
  remove = 0

# All objects are files except service and ldconfig
if args.type != "service" and args.type != "ldconfig":
  if not os.path.exists(args.object[0]):
    print("Error: object", args.object, "does not exist!")
    sys.exit(1)

if args.type == "font":
  if len(args.object) > 1:
    print("Error, too many agurments for type 'font'! Exiting...")
    sys.exit(1)
  else:
    lsbtools.install_font(args.object[0])
elif args.type == "init":
  if len(args.object) > 1:
    print("Error, too many agurments for type 'init'! Exiting...")
    sys.exit(1)
  else:
    lsbtools.install_init(args.object[0])
elif args.type == "profile":
  if len(args.object) > 1:
    print("Error, too many agurments for type 'profile'! Exiting...")
    sys.exit(1)
  else:
    lsbtools.install_profile(args.object[0])
elif args.type == "service":
  if len(args.object) < 2:
    print("Error, too few agurments for type 'service'! Exiting...")
    sys.exit(1)
  else:
    inst_service(args.object)
elif args.type == "inet":
  objecttype = "inet"
elif args.type == "crontab":
  objecttype = "crontab"
elif args.type == "package":
  objecttype = "package"
elif args.type == "menu":
  objecttype = "menu"
elif args.type == "ldconfig":
  objecttype = "ldconfig"
elif args.type == "man":
  objecttype = "man"
else:
  print("Invalid type:", args.type)
  sys.exit(1)

