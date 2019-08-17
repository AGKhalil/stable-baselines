import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def drive_auth():
	# access the drive
	gauth = GoogleAuth()
	# gauth.Authorize()
	return GoogleDrive(gauth) 

def upload_file(drive, full_name):
	directories = full_name.split('/')[:-1]
	filename = full_name.split('/')[-1]
	parent_id = None
	for directory in directories:
		parent_id = upload_directory(drive, directory, parent_id)
	file_list = drive.ListFile({'q':"'%s' in parents and trashed=False" % parent_id}).GetList()
	for file1 in file_list:
		if file1['title'] == filename:
			file1.Delete()
	file = drive.CreateFile({'title': filename, 'parents':[{'id':parent_id}]})
	if filename == 'experiment_logs':
		file.SetContentFile(filename + '.db')
	else:
		file.SetContentFile(full_name)
	file.Upload()

def download_file(drive, full_name, plot=False, db=False):
	names = full_name.split('/')
	_id = None
	for name in names:
		_id = get_id(drive, name, _id)
	downloaded = drive.CreateFile({'id': _id})
	if not plot:
		downloaded.GetContentFile('tmp/tmp_file')
	elif plot and db:
		downloaded.GetContentFile('tmp/tmp_db_file.db')
	else:
		downloaded.GetContentFile('tmp/tmp_plt_file')


def get_id(drive, directory, parent_id=None):
	if parent_id:
		file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent_id}).GetList()
	else:
		file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	for file1 in file_list:
	    if file1['title'] == directory:
	        _id = file1['id']
	return _id

def upload_directory(drive, directory, parent_id=None):
	found_directory = False
	if parent_id:
		file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent_id}).GetList()
	else:
		file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	for file1 in file_list:
	    if file1['title'] == directory:
	        dir_id = file1['id']
	        found_directory = True
	if not found_directory:
		if parent_id:
			top_level_folder = drive.CreateFile({'title': directory, 'parents':[{'id':parent_id}], "mimeType": "application/vnd.google-apps.folder"})
		else:
			top_level_folder = drive.CreateFile({'title': directory, "mimeType": "application/vnd.google-apps.folder"})
		# Upload the file to your drive
		top_level_folder.Upload()
		# Grab the ID of the folder we just created
		dir_id = top_level_folder['id']
	return dir_id

def clean_up(model_path):
	shutil.rmtree(model_path)