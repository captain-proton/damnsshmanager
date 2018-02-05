import pickle
import os


class Store:
    def __init__(self, objects_file):
        self.objects_file = objects_file

    def add(self, obj):

        objs = self.get_all_objects()

        # write new host to pickle file
        with open(self.objects_file, 'wb') as f:
            if objs is None:
                objs = []
            objs.append(obj)
            pickle.dump(objs, f)
            return True

    def delete_objects(self, obj_filter):

        objs = self.get_all_objects()

        with open(self.objects_file, 'wb') as f:

            new_objects = [o for o in objs if obj_filter(o)]
            pickle.dump(new_objects, f)
            if len(objs) != len(new_objects):
                return [o for o in objs if o not in new_objects]

    def unique(self, key):
        objs = self.get_all_objects()

        if objs is not None:
            objs = [o for o in objs if key(o)]
            if len(objs) == 1:
                return objs[0]
        return None

    def get_all_objects(self):
        if not os.path.exists(self.objects_file):
            return None

        with open(self.objects_file, 'rb') as f:
            try:
                hosts = pickle.load(f)
                return hosts
            except EOFError:
                return None
