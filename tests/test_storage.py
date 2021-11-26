import os
import tempfile
import pytest
from damnsshmanager.storage import Store, UniqueException


@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_file = os.path.join(tmpdir, 'damnsshmanager.test.store')
        s = Store(storage_file)
        yield s


def test_unique_exception():
    e = UniqueException('message')
    assert str(e) == 'message'


def test_empty_storage():

    fd, name = tempfile.mkstemp()
    s = Store(name)
    objs = list(s.get(key=lambda: True))
    os.remove(name)
    assert not objs


def test_add(store: Store):
    obj = {'a': 'localhost'}
    obj2 = {'b': '127.0.0.1'}
    store.add(obj)
    store.add(obj2)


def test_get(store: Store):
    obj = {'a': 'localhost'}
    store.add(obj)
    stored_obj = list(store.get(key=lambda o: o['a'] == 'localhost'))
    assert stored_obj and stored_obj[0]['a'] == 'localhost'


def test_unique_missing(store: Store):
    obj = {'a': 'localhost'}
    store.add(obj)
    stored_obj = store.unique(key=lambda o: o['a'] == 'b')
    assert stored_obj is None


def test_unique(store: Store):
    obj = {'a': 'localhost'}
    store.add(obj)
    stored_obj = store.unique(key=lambda o: o['a'] == 'localhost')
    assert stored_obj


def test_unique_multiple(store: Store):
    obj = {'a': 'localhost'}
    store.add(obj)
    store.add(obj)
    with pytest.raises(UniqueException):
        store.unique(key=lambda o: o['a'] == 'localhost')


def test_delete(store: Store):
    obj = {'a': 'localhost'}
    obj2 = {'b': '127.0.0.1'}
    store.add(obj)
    store.add(obj2)

    def key_func(o):
        return o.get('a') == 'localhost'

    store.delete(key_func)
    stored_obj = list(store.get(key=key_func))
    assert not stored_obj
