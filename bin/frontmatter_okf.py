#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["argparse", "python-frontmatter", "pyyaml"]
# ///
#
# utility to update frontmatter with [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) data
#

import argparse
from datetime import datetime, timezone
import sys
import frontmatter
import os
import subprocess

default_path = os.path.join(os.path.dirname(__file__), "..", "src", "content", "logos")

parser = argparse.ArgumentParser()
parser.add_argument("--directory", help="directory with logo subdirectories", action="store", default=default_path)
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")

args = parser.parse_args()

def get_git_first_modified_iso_utc(file_path):
	"""Return first git commit time for a file as UTC ISO-8601, or None if unavailable."""
	git_dir = os.path.dirname(file_path)
	try:
		result = subprocess.run(
			["git", "-C", git_dir, "log", "--follow", "--format=%ct", "--", file_path],
			capture_output=True,
			text=True,
			check=False,
		)
		if result.returncode != 0:
			return None

		all_revisions = [line.strip() for line in result.stdout.splitlines() if line.strip()]
		if not all_revisions:
			return None

		# git log returns newest -> oldest; oldest is the last line.
		unix_ts = all_revisions[-1]

		dt = datetime.fromtimestamp(int(unix_ts), tz=timezone.utc)
		return dt.isoformat().replace("+00:00", "Z")
	except (ValueError, OSError):
		return None

def process(options, dirparam):
	logodir = os.path.abspath(dirparam)
	logohandle = os.path.basename(logodir)

	logo = os.path.join(logodir, logohandle + "-ar21.svg")
	if os.path.exists(logo) == False:
		# There is only a placeholder, so skip
		return

	indexfn = os.path.join(logodir, "index.md")
	if os.path.exists(indexfn) == False:
		print("ERROR: no index.md for %s" % logohandle)
		return


	dirty = False
	indexmd = frontmatter.load(indexfn)

	if "title" not in indexmd.keys():
		print("ERROR: no title in frontmatter" % logohandle)
		return

	if "resource" not in indexmd.keys():
		indexmd["resource"] = "https://www.vectorlogozone.com/logos/%s/%s-ar21.svg" % (logohandle, logohandle)
		dirty = True

	if "timestamp" not in indexmd.keys():
		# get the first modified time of the logo file from git
		git_timestamp = get_git_first_modified_iso_utc(logo)
		if git_timestamp is None:
			print("WARNING: unable to get git timestamp for %s, using current time" % logohandle)
			git_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

		indexmd["timestamp"] = git_timestamp
		dirty = True
		#print("INFO: timestamp for %s set to %s" % (logo, indexmd["timestamp"]))

	if "type" not in indexmd.keys() or indexmd["type"] != "Logo":
		indexmd["type"] = "Logo"
		dirty = True

	if dirty:
		print("INFO: updating frontmatter for %s" % logohandle)
		f = open(indexfn, 'w')
		f.write(frontmatter.dumps(indexmd))
		f.write('\n')
		f.close()

sys.stdout.write("INFO: frontmatter okf started at %s\n" % datetime.now(timezone.utc).isoformat())

logoroot = args.directory
sys.stdout.write("INFO: processing directory %s\n" % logoroot)

dirs = [f for f in os.listdir(logoroot) if os.path.isdir(os.path.join(logoroot, f))]
dirs.sort()
sys.stdout.write("INFO: %d directories found\n" % len(dirs))

for logodir in dirs:
	#print("INFO: procssing %s" % logodir)
	process('', os.path.join(logoroot, logodir))

sys.stdout.write("INFO: frontmatter okf completed at %s\n" % datetime.now(timezone.utc).isoformat())
