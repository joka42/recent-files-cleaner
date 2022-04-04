#!/usr/bin/python

import sys
import os
import time
import logging
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.etree.ElementTree as ET


class MyHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        FileSystemEventHandler.__init__(self)
        self.counter = 0
        self.file_path = file_path
        self.pattern = re.compile("[a-zA-Z0-9]\/\.[a-zA-Z0-9].")
        self.clean_content(False)

    def on_moved(self, event):
        if event.is_directory:
            return

        if self.file_path != event.dest_path:
            return

        print(f"{self.counter}: {event.dest_path}")
        self.clean_content(True)
        self.counter += 1

    def clean_content(self, only_last=False):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        bookmarks = root.findall('bookmark')

        if only_last:
            bookmarks = bookmarks[-1:]

        changed = False
        for bookmark in bookmarks:
            path = bookmark.attrib['href']
            res = re.search(self.pattern, path)
            if res:
                root.remove(bookmark)
                changed = True
                print("Match!")
        if changed:
            tree.write(self.file_path)


if __name__ == "__main__":
    path = os.path.join(os.environ["HOME"], ".local", "share")
    observer = Observer()
    handler = MyHandler(os.path.join(path, "recently-used.xbel"))
    observer.schedule(handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()