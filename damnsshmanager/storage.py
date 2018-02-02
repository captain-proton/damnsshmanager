import pickle
import os


def add(objects_file, obj):

    objs = get_all_objects(objects_file)

    # write new host to pickle file
    with open(objects_file, 'wb') as f:
        if objs is None:
            objs = []
        objs.append(obj)
        pickle.dump(objs, f)
        return True


def delete_objects(objects_file, obj_filter):

    objs = get_all_objects(objects_file)

    with open(objects_file, 'wb') as f:

        new_objects = [o for o in objs if obj_filter(o)]
        pickle.dump(new_objects, f)
        if len(objs) != len(new_objects):
            return [o for o in objs if o not in new_objects]


def unique(objects_file, key):
    objs = get_all_objects(objects_file)

    if objs is not None:
        objs = [o for o in objs if key(o)]
        if len(objs) == 1:
            return objs[0]
    return None


def get_all_objects(objects_file):
    if not os.path.exists(objects_file):
        return None

    with open(objects_file, 'rb') as f:
        try:
            hosts = pickle.load(f)
            return hosts
        except EOFError:
            return None
