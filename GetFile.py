def GetFile():
	import os
	#filename of target file here
	filename = raw_input("Enter file to shred:	")

	#check file exists
	while((os.path.exists(filename)) != True):
		print'Error: file \"', filename, '\" does not exist'
		filename = ""
		filename = raw_input("Enter file to shred:	")

	#return value
	return filename
