import abc
import os
import pathlib
import pickle
import shutil
import tempfile
from typing import Any, Iterable, Optional, Union

from loguru import logger

from damnsshmanager.config import Config
from damnsshmanager.model import Host, LocalTunnel


class Store(abc.ABC):

    @property
    @abc.abstractmethod
    def object_file(self) -> pathlib.Path:
        ...

    @abc.abstractmethod
    def __init__(self, src: pathlib.Path):
        ...

    @abc.abstractmethod
    def add(self, obj: Union[Host, LocalTunnel], sort=None):
        ...

    @abc.abstractmethod
    def get(self, key) -> Iterable:
        ...

    @abc.abstractmethod
    def delete(self, obj: Union[Host, LocalTunnel]):
        ...

    @abc.abstractmethod
    def unique(self, key) -> Optional[Any]:
        ...


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


def backup(func):
    """Decorator that can be used to backup a Store objects file.

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

    def wrapper(store: Store, *args, **kwargs):
        def rollback(src, dst):
            if os.path.exists(dst):
                os.remove(dst)
            if os.path.exists(src):
                shutil.move(src, dst)

        run_with_backup = os.path.exists(store.object_file)
        if not run_with_backup:
            return func(*args, **kwargs)

        # if a backup is required run with all the stuff of copy
        # move, remove and so on, otherwise just call the function
        backup_file = tempfile.TemporaryFile(mode="w+b")
        func_result = None
        with open(store.object_file, "r+b") as f:
            shutil.copyfileobj(f, backup_file)
            backup_file.seek(0)

            try:
                func_result = func(store, *args, **kwargs)
            except IOError:
                rollback(backup_file.name, store.object_file)
        return func_result

    return wrapper


class PickleStore:
    """A `Store` allows crud (create, read, update, delete) operations
    on a file to persist python objects.

    Attributes
    ----------
    object_file : str
        Contains the file path that objects are stored in
    """

    def __init__(self, object_file: pathlib.Path):
        self.__object_file = object_file

    def __empty(self):
        yield from ()

    @property
    def object_file(self):
        return self.__object_file

    @backup
    def add(self, obj: Union[Host, LocalTunnel], sort=None):
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
            with open(self.__object_file, "wb") as f:

                objs.append(obj)
                if sort:
                    objs = sorted(objs, key=sort)
                pickle.dump(objs, f)
        except IOError as err:
            logger.error(Config.messages.get("err.msg.dump.error",
                                             self.__object_file))
            raise err

    @backup
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

        with open(self.__object_file, "wb") as f:

            new_objects = [o for o in objs if not func(o)]
            pickle.dump(new_objects, f)
            if len(objs) != len(new_objects):
                return [o for o in objs if o not in new_objects]
        return []

    def unique(self, key) -> Optional[Any]:
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
            if size > 1:
                raise UniqueException(
                    f"found {{size}} objects that match in {self.__object_file}"
                )
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
        if not os.path.exists(self.__object_file):
            return self.__empty()

        with open(self.__object_file, "rb") as f:
            try:
                objs = pickle.load(f)
                if objs:
                    return filter(key, objs)
            except EOFError:
                return self.__empty()

        return self.__empty()


Store.register(PickleStore)
