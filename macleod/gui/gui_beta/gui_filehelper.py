from os import path


class GuiFileHelper:
    def __init__(self):
        self.hashes = dict()
        self.paths = dict()

    def add_path(self, ui_element, file_path):
        """
        Keep track of a file that's been open
        """

        self.paths.update({ui_element: None if file_path is None else path.normpath(file_path)})

    def update_path(self, ui_element, file_path):
        """
        Change the path to the currently opened file
        """

        self.paths[ui_element] = path.normpath(file_path)

    def get_path(self, ui_element):
        """
        Get the path matching the current file
        If it's a new file, return None
        """
        if not self.paths.__contains__(ui_element):
            return None
        return self.paths[ui_element]

    def remove_key(self, ui_element):
        """
        Call this when you close a file
        """
        self.hashes.pop(ui_element, None)
        self.paths.pop(ui_element, None)

    def add_clean_hash(self, text_element, plain_text):
        """
        The hash is a hash of the plain text
        """
        self.hashes.update({text_element: hash(plain_text)})

    def update_clean_hash(self, ui_element, plain_text):
        """
        Only call after add_clean_hash
        """

        self.hashes[ui_element] = hash(plain_text)

    def is_dirty(self, text_element, plain_text):
        """
        True if the file is dirty or the file is new
        False otherwise
        """
        if not self.hashes.__contains__(text_element):
            return True
        return self.hashes[text_element] != hash(plain_text)
