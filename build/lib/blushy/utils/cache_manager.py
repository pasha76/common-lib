import pickle
import os
import datetime

class FileSystemCache():
    def __init__(self, folder_path):
        self.file_name = os.path.join(folder_path, "cache.txt")
        # create file if not exist and initialize it with empty dict
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'wb') as f:
                initial = {}
                pickle.dump(initial, f)

    def get(self, key):
        if not self.has(key):
            return None
        dict_obj = self.__get_file_content()

        row = dict_obj.get(key)

        if self.__is_expired_row(row):
            self.delete(key)
            return None

        return row['value']

    def has(self, key):
        dict_obj = self.__get_file_content()

        if key in dict_obj:
            # check expiration before returning true
            row = dict_obj.get(key)

            if self.__is_expired_row(row):
                self.delete(key)
                return False
            return True

        return False

    def delete(self, key):
        dict_obj = self.__get_file_content()

        if key in dict_obj:
            dict_obj.pop(key)

        self.__put_file_content(dict_obj)

    def update(self, key, value, lifespan=3600):
        dict_obj = self.__get_file_content()

        dict_obj[key] = {
            'value': value,
            '_created_at': datetime.datetime.now(),
            '_lifetime': lifespan
        }
        
        self.__put_file_content(dict_obj)

    def add(self, key, value, lifespan=3600):
        dict_obj = self.__get_file_content()

        if key not in dict_obj:
            dict_obj[key] = {
                'value': value,
                '_created_at': datetime.datetime.now(),
                '_lifetime': lifespan
            }
        
        self.__put_file_content(dict_obj)

    def inc(self, key, delta=1):
        dict_obj = self.__get_file_content()

        if key in dict_obj:
            row = dict_obj.get(key)

            if isinstance(row['value'], int):
                dict_obj[key]['value'] += delta
                self.__put_file_content(dict_obj)

    def reset(self):
        dict_obj = {}
        self.__put_file_content(dict_obj)

    # private methods
    def __get_file_content(self):
        try:
            with open(self.file_name, 'rb') as f:
                return pickle.load(f)
        except (IOError, EOFError) as e:
            print(f"Error reading cache file: {str(e)}")  # More detailed error logging
            if os.path.exists(self.file_name):
                print(f"Cache file exists but is corrupted. File size: {os.path.getsize(self.file_name)}")
            return {}

    def __put_file_content(self, new_content):
        try:
            # Write to temporary file first
            temp_file = f"{self.file_name}.tmp"
            with open(temp_file, 'wb') as f:
                pickle.dump(new_content, f)
            # Then atomically rename it
            os.replace(temp_file, self.file_name)
        except IOError as e:
            print(f"Error writing to cache file: {str(e)}")

    def __is_expired_row(self, row):
        # check expiration date and if passed 
        _created_at = row['_created_at']
        # total amount of seconds for the existence of the stored value
        _lifetime = row['_lifetime']

        diff = datetime.datetime.now() - _created_at

        in_seconds = diff.total_seconds()

        return in_seconds > _lifetime
    
    def create_or_update(self, key, func, **params):
        if self.has(key):
            print("Cache hit")
            return self.get(key)
        else:
            value = func(**params)
            print(params)
            self.add(key, value,60*15)
            return value