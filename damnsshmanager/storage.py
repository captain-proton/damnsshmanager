import pickle
import os
import shutil
import tempfile
from typing import Iterable

from loguru import logger
from damnsshmanager.config import Config


class UniqueException(Exception):
    """Exception raised for unique object errors

    Attributes
    ----------
    message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Store(object):
    """A `Store` allows crud (create, read, update, delete) operations
    on a file to persist python objects.

    Attributes
    ----------
    objects_file : str
        Contains the file path that objects are stored in
    """

    def __init__(self, objects_file):
        self.objects_file = objects_file

    def __empty(self):
        yield from ()

    def __backup(func):
        """Decorator that can be used to backup this objects file.

        A function annotated with this decorator must return a value
        that evaluates to True on conditional check, otherwise the
        original file will be overridden.

        The backup file will be inside the same directory with a suffix
        of .0 until .255 in case multiple files were found.

        In case the backup could not be created, the function is called
        as wanted and not blocked!

        Parameters
        ----------

        A function that returns a value that evaluates to True or False
        on a conditional check
        """

        def wrapper(self, *args, **kwargs):

            def rollback(src, dst):
                if os.path.exists(dst):
                    os.remove(dst)
                if os.path.exists(src):
                    shutil.move(src, dst)

            run_with_backup = os.path.exists(self.objects_file)
            if not run_with_backup:
                return func(self, *args, **kwargs)

            # if a backup is required run with all the stuff of copy
            # move, remove and so on, otherwise just call the function
            backup_file = tempfile.TemporaryFile(mode='w+b')
            with open(self.objects_file, 'r+b') as f:
                shutil.copyfileobj(f, backup_file)
                backup_file.seek(0)

                try:
                    func_result = func(self, *args, **kwargs)
                except IOError:
                    rollback(backup_file.name, self.objects_file)
            return func_result

        return wrapper

    @__backup
    def add(self, obj, sort=None):
        """Adds a new object to the store.

        Parameters
        ----------
        obj : object
            Any python object
        sort : function(object)
            Function that is used by sorted(list, key=x) as key

        Returns
        -------
        bool
            True if the object was added to the store, False otherwise
        """
        objs = self.get()
        objs = list(objs) if objs else []

        # write new host to pickle file
        try:
            with open(self.objects_file, 'wb') as f:

                objs.append(obj)
                if sort:
                    objs = sorted(objs, key=sort)
                pickle.dump(objs, f)
        except IOError as e:
            logger.error(Config.messages.get('err.msg.dump.error',
                                             self.objects_file))
            raise e

    def delete(self, func):
        """Delete all objects that the given filter applies to.

        Example
        -------
        from damnsshmanager.storage import Store
        store = Store('~/.damnsshmanager/hosts.pickle')
        store.delete(lambda o: o.alias == alias)

        Parameters
        ----------
        func : callable
            Any callable function, lambda or whatever that takes one parameter
            that will be the object which may be removed

        Returns
        -------
        A list with all deleted objects or None if no objects where deleted
        """
        objs = self.get()
        objs = list(objs) if objs else []

        with open(self.objects_file, 'wb') as f:

            new_objects = [o for o in objs if not func(o)]
            pickle.dump(new_objects, f)
            if len(objs) != len(new_objects):
                return [o for o in objs if o not in new_objects]

    def unique(self, key):
        """Return the one object that matches given key function(item).

        Example
        -------
        from damnsshmanager.storage import Store
        store = Store('~/.damnsshmanager/hosts.pickle')
        store.unique(key=lambda o: o.alias == alias)

        Parameters
        ----------
        key : function(item)
            Any callable function, lambda or whatever that takes one parameter
            that will be the object which may match

        Returns
        -------
        The objects that matches the key or None if nothing could be found

        Raises
        ------
        UniqueException
            If more than one object was found for given key
        """
        filtered = self.get(key)
        if filtered:
            objs = list(filtered)
            size = len(objs)
            if size == 1:
                return objs[0]
            elif size > 1:
                raise UniqueException('found %d objects that match in %s' %
                                      (size, self.objects_file))
        return None

    def get(self, key=None) -> Iterable:
        """Return all objects of this store that apply to given key.

        Example
        -------
        from damnsshmanager.storage import Store
        store = Store('~/.damnsshmanager/hosts.pickle')
        store.get(key=lambda o: o.alias == alias)

        kwargs
        ------
        key : callable
            Any callable function, lambda or whatever that takes one parameter
            that will be the object which may match

        Returns
        -------
        The result of filter(function or None, items), therefore an iterator
        yielding the results or None
        """
        if not os.path.exists(self.objects_file):
            return self.__empty()

        with open(self.objects_file, 'rb') as f:
            try:
                objs = pickle.load(f)
                if objs:
                    return filter(key, objs)
            except EOFError:
                return self.__empty()

        return self.__empty()
