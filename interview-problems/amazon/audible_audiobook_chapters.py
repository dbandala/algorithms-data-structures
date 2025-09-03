# Design a data structure to efficiently store and retrieve audiobook chapters and their corresponding timestamps.

class Chapter:
    def __init__(self, title, start_time, end_time):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time

class Audiobook:
    def __init__(self):
        self.chapters = []
        self.chapter_map = {}

    def add_chapter(self, title, start_time, end_time):
        chapter = Chapter(title, start_time, end_time)
        self.chapters.append(chapter)
        self.chapter_map[title] = chapter

    def get_chapter(self, title):
        return self.chapter_map.get(title)

    def get_all_chapters(self):
        return self.chapters

    def delete_chapter(self, title):
        chapter = self.chapter_map.pop(title, None)
        if chapter:
            self.chapters.remove(chapter)
