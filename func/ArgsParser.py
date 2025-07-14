import argparse
import os
import sys

parser = argparse.ArgumentParser(
    prog='MinecraftLauncher',
    epilog='Use this to work with the launcher without launching the UI',
    add_help=False)

parser.add_argument("-h", "--help",
    action="store_true",
    help="Displays the command help message")

parser.add_argument("--nostart",
    action="store_true",
    help="Does not start the launcher after executing the command")

parser.add_argument("--nogui",
    action="store_true",
    help="Execute the action without launching the UI")

parser.add_argument("--debug",
    action="store_true",
    help="No close console window")

parser.add_argument("-swbn", "--start-with-build-name",
    metavar="<BuildName-str>",
    type=str,
    help="Starts the build by its name")

parser.add_argument("-a", "--all-builds",
    action="store_true",
    help="Displays all information about the builds")

parser.add_argument("-sff", "--start-from-folder",
    metavar=("<path-str>", "<MCVer-str>", "<Core-str>", "<CoreVer-str>", "<Nickname-str>"),
    nargs=5,
    type=str,
    help="Starts a build from the specified path (not tracked by the launcher)")

parser.add_argument("-p", "--profile",
    action="store_true",
    help="Displays information about the selected profile")

parser.add_argument("-sp", "--set-profile",
    metavar="<ProfileIndex-int>",
    type=int,
    help="Sets the profile by index")

parser.add_argument("-MCClose", "--close-by-name",
    metavar="<BuildName-str>",
    type=str,
    help="Forcibly closes the client by build name")

parser.add_argument("-i", "--install-core",
    metavar=("<Core-str>", "<CoreVer-str>", "<MCVer-str>"),
    nargs=3,
    type=str,
    help="Downloads the selected version of the core")

args = parser.parse_args()
if args.help:
    parser.print_help()
    sys.exit(0)

default = {'swbn': None, 'sff': None, 'MCClose': None, 'instcore': None, 'nogui': False, 'nomsg': False, 'getAllBuilds': None, "debug": args.debug}

msg = {
    "swbn": args.start_with_build_name,
    "sff": args.start_from_folder,
    "MCClose": args.close_by_name,
    "instcore": args.install_core,
    "nogui": bool(args.nogui),
    "getAllBuilds": bool(args.all_builds),
    "nostart": args.nostart,
    "p": args.profile,
    "sp": args.set_profile,
    "debug": args.debug
}
