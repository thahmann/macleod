from os import path

class GUI_file_helper():
    def __init__(self):
        self.hashes = dict()
        self.paths = dict()

    def add_path(self, UI_element, file_path):
        self.paths.update({UI_element : None if file_path is None else path.normpath(file_path)})

    def update_path(self, UI_element, file_path):
        self.paths[UI_element] = path.normpath(file_path)

    def contains_path(self, path):
        return path in self.paths.values()

    def get_path(self, UI_element):
        if not self.paths.__contains__(UI_element):
            return None
        return self.paths[UI_element]

    def remove_key(self, UI_element):
        self.hashes.pop(UI_element, None)
        self.paths.pop(UI_element, None)

    def add_clean_hash(self, text_element, plain_text):
        self.hashes.update({text_element : hash(plain_text)})

    def update_clean_hash(self, UI_element, plain_text):
        self.hashes[UI_element] = hash(plain_text)

    def is_dirty(self, text_element, plain_text):
        if not self.hashes.__contains__(text_element):
            return True
        return self.hashes[text_element] != hash(plain_text)
