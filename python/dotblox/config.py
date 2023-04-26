import copy
import json
import os
import sys


class ConfigIO(object):
    def __init__(self, file_path, read, write, default=None, sync=True):
        """File IO class for contextual reading and writing of a
        configuration file

        Args:
            file_path (str): file path to the config file
            read (func): the function used when reading the file
            write (func): the function to use when writing the file
            default (dict): the default data to cache when the file
                            doesnt exist.
            sync (bool): when data is read the latest is pulled from the file.
                         when data is written the file is updated on disk.

        Usage:
            io = ConfigIO(file_path, read, write)
            with io as data:
                current_data = data

            with io.write() as data:
                data["key"] = value

        """
        self.file_path = file_path
        self.modified_time = 0
        self.__context_write = False
        self._sync = sync
        self._io_read = read
        self._io_write = write

        if default is None:
            default = {}

        self.cache = {}
        self.default_data = default

    def save_to_disk(self):
        try:
            with open(self.file_path, "w") as f:
                self._io_write(f, self.cache)
        except:
            print("Unable to save to " + self.file_path)

    def read_from_disk(self, force=False):
        """Read the file from disk.

        This checks the modified time of the file as to avoid subsequent
        reads

        Args:
            force (bool): forces a read from disk even if the modified
                           time is the same

        Returns:
            dict: data from the configuration
        """
        if not os.path.exists(self.file_path):
            self.cache = copy.copy(self.default_data)
            return

        last_modified = os.path.getmtime(self.file_path)
        if self.modified_time < last_modified or force:
            self.modified_time = last_modified
            with open(self.file_path, "r") as f:
                self.cache = self._io_read(f)

    def __enter__(self):
        if self._sync:
            self.read_from_disk()
        return self.cache

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__context_write and self._sync:
            self.save_to_disk()

    def write(self):
        """Use in a with statement to auto save the file when sync is on"""
        self.__context_write = True
        return self

    def pause_sync(self):
        """Pause syncing"""
        self._sync = False

    def start_sync(self, save=False):
        """Start sync and save current to file if given

        Args:
            save (bool): save the file when stating the syc

        """
        self._sync = True
        if save:
            self.save_to_disk()


class BaseConfig(object):
    def __init__(self, path, default=None):
        """Base class for config files.

        _io_read and io_write must be implemented in subsequent classes

        Args:
            path (str): the fie path of the config
            default (dict): default data to fill the file
        """
        self.path = path
        self.io = ConfigIO(path, self._io_read, self._io_write, default=default)
        self.io.read_from_disk()

    def _io_read(self, f):
        """The function to be used when reading the file

        Args:
            f (file): the file object passed through

        Returns:
            dict: the data to be cached
        """
        raise NotImplementedError("%s._io_read must be implented" % self.__class__.__name__)

    def _io_write(self, f, data):
        """The function to be used when writing the file

        Args:
            f (file): the file object passed through
        """
        raise NotImplementedError("%s._io_write must be implented" % self.__class__.__name__)

    def pause_sync(self):
        """Pause the io syncing"""
        self.io.pause_sync()

    def is_paused(self):
        """Check is io is syncing with changes"""
        return not self.io._sync

    def start_sync(self, save=False):
        """Start syncing with file changes"""
        self.io.start_sync(save=save)

    def save(self):
        """Save current contents to disk"""
        self.io.save_to_disk()

    def __eq__(self, other):
        return self.path == other or self != other

    def revert(self):
        """Revert the file from the current contents on disk"""
        self.io.read_from_disk(force=True)


class ConfigJSON(BaseConfig):
    def __init__(self, path, default=None):
        """Base Class for reading and writing a json file

        This class is meant to be inherited.

        Usage:
            class Settings(ConfigJSON):
                def get_data(self):
                    with self.io as data:
                        return data
                def set_data(self, data)
                    with self.io.write() as data:
                        data.update(data)

        """
        BaseConfig.__init__(self, path, default)

    def _io_read(self, f):
        return json.load(f)

    def _io_write(self, f, data):
        json.dump(data, f, indent=4)


def _path_find_generator(name, include_global=False, global_priority=False):
    """Search for a config given the file name along sys.path

    Args:
        name (str): exact file name to search for

    Returns:
        generator: generator object holding the paths
    """
    paths = get_config_paths(include_global=include_global, global_priority=global_priority)

    for path in paths:

        config_path = os.path.join(path, name)
        config_path = config_path.replace("\\", '/')
        if not os.path.exists(config_path):
            continue

        yield config_path


def find_all(name, include_global=False, global_priority=False):
    """Find all configs with the given name along sys.path

    Args:
        name (str): Name of file including the extension
    """
    return list(_path_find_generator(name,
                                     include_global=include_global,
                                     global_priority=global_priority))


def find_one(name, include_global=False, global_priority=False):
    """Find the first config with the given name along sys.path

    Args:
        name (str): Name of file including the extension
    """
    try:
        return next(_path_find_generator(name,
                                         include_global=include_global,
                                         global_priority=global_priority))
    except StopIteration:
        return None

def is_findable(path, include_global=False):
    """Ensure a generated config is findable on the path"""
    parent = os.path.dirname(path).replace("\\", "/")
    paths = get_config_paths(include_global=include_global)
    return parent in paths

def get_config_paths(include_global=False, global_priority=False):
    """Get all paths along PYTHONPATH

    Args:
        include_global (bool): Include the dotbox global settings path
            in the results
        global_priority (bool): Choose to prepend/append the global path.
            Default appends.

    Returns:
        list[str]: list of system paths
    """
    result = []

    for path in sys.path:
        # Sanitize paths just in case
        path = path.replace("\\", '/')
        # In case sys.path has multiples and has different slashes in the path
        if path in result:
            continue
        result.append(path)

    if include_global:
        global_root = get_global_settings_folder(False)
        if global_priority:
            result.insert(0, global_root)
        else:
            result.append(global_root)

    return result

def get_global_settings_folder(create=True):
    """Get the users home directory with the .dotblox directory

    Args:
        create (bool): Creates the folder on disk when queried

    Returns:
        str: path to directory
    """
    user_path = os.path.expanduser("~")
    if user_path.endswith("Documents"):
        user_path = os.path.dirname(user_path)
    settings_path = os.path.join(user_path, ".dotblox")
    if create and not os.path.exists(settings_path):
        os.mkdir(settings_path)
    return settings_path.replace("\\", "/")

def get_global_settings_file(file_name, parent=None, create=True, create_folder=True):
    """Create any file in the global settings folder

    Args:
        file_name (str): Name of the file with extension.
        create (bool): Create the file on disk.
        create_folder (bool): Create the global settings directory.
        parent: Add a parent folder to the path.

    Returns:
        str: path to
    """
    settings_folder = get_global_settings_folder(create_folder)

    if parent:
        settings_folder = os.path.join(settings_folder, parent)
        if create and os.path.exists(settings_folder):
            os.mkdir(settings_folder)

    settings_file = os.path.join(settings_folder, file_name)

    if create and not os.path.exists(settings_file):
        if not os.path.exists(settings_folder):
            raise Exception("Unable to create file because parent "
                            "folder has not been created. Set create_folder to True")

        with open(settings_file, 'w') as _:
            pass
    return settings_file
