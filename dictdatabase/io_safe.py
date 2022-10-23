import os
from . locking import ReadLock, WriteLock
from . import config, utils, io_unsafe


def read(db_name: str):
	"""
		Ensure that reading only starts when there is no writing,
		and that while reading, no writing will happen.
		Otherwise, wait.
	"""

	_, json_exists, _, ddb_exists = utils.db_paths(db_name)
	if not json_exists and not ddb_exists:
		return None
	# Wait in any write lock case, "need" or "has".
	lock = ReadLock(db_name)
	res = io_unsafe.read(db_name)
	lock.unlock()
	return res


def write(db_name: str, db: dict):
	"""
		Ensures that writing only starts if there is no reading or writing in progress.
	"""
	dirname = os.path.dirname(f"{config.storage_directory}/{db_name}.any")
	os.makedirs(dirname, exist_ok=True)

	write_lock = WriteLock(db_name)
	io_unsafe.write(db_name, db)
	write_lock.unlock()


def delete(db_name: str):
	"""
		Ensures that deleting only starts if there is no reading or writing in progress.
	"""
	json_path, json_exists, ddb_path, ddb_exists = utils.db_paths(db_name)
	if not json_exists and not ddb_exists:
		return None
	write_lock = WriteLock(db_name)
	if json_exists:
		os.remove(json_path)
	if ddb_exists:
		os.remove(ddb_path)
	write_lock.unlock()