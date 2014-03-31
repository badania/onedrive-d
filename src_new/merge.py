#!/usr/bin/python

# Merge local and remote OneDrive repo
# Warning: Rely heavily on system time and if the timestamp is screwed there may be unwanted file deletions.

import sys, os, subprocess, yaml

# OneDriveEntry represents either a file entry or a dir entry in the OneDrive repository
class OneDriveEntry:
	_raw_log = []
	_ent_list = []
	_remotePath = ""
	_localPath = ""
	
	def __init__(self, localPath, remotePath):
		self._localPath = localPath
		self._remotePath = remotePath
		print "Start merging dir " + remotePath + " (locally at \"" + localPath + "\")"
		self.ls()
	
	def ls(self):
		subp = subprocess.Popen(['skydrive-cli', 'ls', '--objects', self._remotePath], stdout=subprocess.PIPE)
		log = subp.communicate()[0]
		self._raw_log = yaml.safe_load(log)
	
	# list the current dirs and files in the local repo, and in merge() upload / delete entries accordingly
	def pre_merge(self):
		# if remote repo has a dir that does not exist locally
		# make it and start merging
		if not os.path.exists(self._localPath):
			try:
				os.mkdir(self._localPath)
			except OSError as exc: 
					if exc.errno == errno.EEXIST and os.path.isdir(self._localPath):
						pass
		else:
			# if the local path exists, record what is in the local path
			self._ent_list = os.listdir(self._localPath)
	
	# recursively merge the remote files and dirs into local repo
	def merge(self):
		self.pre_merge()
		
		if self._raw_log == None:
			return
		for entry in self._raw_log:
			if os.path.exists(self._localPath + "/" + entry["name"]):
				print "Oops, " + self._localPath + "/" + entry["name"] + " exists."
				# do some merge
				self.checkout(entry)
				# after sync-ing
				del self._ent_list[self._ent_list.index(entry["name"])] # remove the ent from untouched list
			else:
				print "Wow, " + self._localPath + "/" + entry["name"] + " does not exist."
				self.checkout(entry)
		
		self.post_merge()
	
	# checkout one entry, either a dir or a file, from the log
	def checkout(self, entry, isExistent = False):
		if entry["type"] == "file" or entry["type"] == "photo" or entry["type"] == "audio" or entry["type"] == "video":
			print "Syncing file " + self._localPath + "/" + entry["name"]
			
		else:
			print "Syncing dir " + self._localPath + "/" + entry["name"]
			ent = OneDriveEntry(self._localPath + "/" + entry["name"], self._remotePath + "/" + entry["name"])
			ent.merge()
	
	# download a file to localPath
	def get_file(self, entry):
		pass
	
	# upload a file to remotePath
	def put_file(self, entry):
		pass
	
	# remove a file from remotePath
	def rm_file(self, entry):
		pass
	
	# make a dir to remotePath
	def mk_dir(self, ent_stat):
		pass
	
	# note: mv, cp, and del will be handled by daemon rather than this sync script
	
	# process untouched files during merge
	def post_merge(self):
		# there is untouched item in current dir
		if self._ent_list != []:
			print "The following items are untouched yet:\n" + str(self._ent_list)
			# so handle them!
		# print something so I know what happened.
		self.debug()
	
	# print the internal storage
	def debug(self):
		print "localPath: " + self._localPath + ""
		print "remotePath: " + self._remotePath + ""
		print self._raw_log
		print "\n"
		print self._ent_list
		print "\n"
	
CONF_PATH = "~/.onedrive"

f = open(os.path.expanduser(CONF_PATH + "/user.conf"), "r")
CONF = yaml.safe_load(f)
f.close()

rootDir = OneDriveEntry(CONF["rootPath"], "")
rootDir.merge()