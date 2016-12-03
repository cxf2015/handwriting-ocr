import glob
import xml.etree.ElementTree as ET
from random import shuffle

import cairo


class Word(object):
    def __init__(self, text, id):
        self.text = text
        self.id = id

    def filename(self):
        split = self.id.split("-")
        return "{}/{}-{}/{}-{}-{}-{}.png".format(split[0], split[0], split[1], split[0], split[1], split[2], split[3])

    def




class SentenceReader(object):

    def __init__(self):
        self.words = []
        files = glob.glob("data/xml/*.xml")
        for file in files:
            tree = ET.parse(file)
            root = tree.getroot()
            wordElements = root.findall('.//word')
            for wordElement in wordElements:
                self.words.append(Word(wordElement.attrib['text'], wordElement.attrib['id']))
        shuffle(self.words)

    def sentences(self, num_words, max_chars_per_word):
        for word in self.words[:num_words]:
            yield word.filename()

def file_to_vector(filename):
    cairo
    image_surface_create_from_png

print([filename for filename in SentenceReader().sentences(10, 2)])
