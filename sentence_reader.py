import glob
import os
import xml.etree.ElementTree as ET
from random import shuffle

import cairocffi as cairo
import numpy as np
from scipy import ndimage
from scipy.misc import imread, imsave


class Sentence(object):
    def __init__(self, text, id, file_prefix='sentences'):
        self.text = text
        self.id = id
        self.file_prefix = file_prefix

    def get_text(self):
        return self.text

    def create_image_surface(self):
        return cairo.ImageSurface.create_from_png(self.get_filename())

    def get_image_data(self, height, width):
        a = imread(self.get_filename(), True, 'L')
        image_height, image_width = a.shape
        border_width, border_height = (10, 16)
        if image_width + border_width > width or image_height + border_height > height:
            raise IOError(
                'is too large for given image size {}, {}'.format((image_height, image_width), (height, width)))

        max_shift_x = width - image_width - border_width
        max_shift_y = height - image_height - border_height
        left_pad = np.random.randint(0, int(max_shift_x))
        right_pad = width - (left_pad + image_width)
        top_pad = np.random.randint(0, int(max_shift_y))
        bottom_pad = height - (top_pad + image_height)

        a = np.pad(a, ((top_pad, bottom_pad), (left_pad, right_pad)), 'constant', constant_values=255)

        a = a.astype(np.float32) / 255

        a = np.expand_dims(a, 0)
        a = speckle(a)

        imsave("/tmp/output.png", a[0])
        return a[0]

    def get_image_height(self):
        return self.create_image_surface().get_height()

    def get_image_width(self):
        return self.create_image_surface().get_width()

    def get_filename(self):
        split = self.id.split("-")
        return "data/{}/{}/{}-{}/{}-{}-{}-{}.png".format(self.file_prefix, split[0], split[0], split[1], split[0],
                                                         split[1], split[2], split[3])

    def get_num_words(self):
        return len(self.text.split(" "))


class Word(Sentence):
    def __init__(self, text, id):
        Sentence.__init__(self, text, id, 'words')


class SentenceReader(object):
    def __init__(self):
        self.sentences = []
        files = glob.glob("data/xml/a01*.xml")
        for file in files:
            tree = ET.parse(file)
            root = tree.getroot()
            wordElements = root.findall('.//word')
            for wordElement in wordElements:
                word = Word(wordElement.attrib['text'], wordElement.attrib['id'])
                if (os.path.getsize(word.get_filename()) > 0):
                    self.sentences.append(word)
        shuffle(self.sentences)

    def sentence_generator(self):
        for sentence in self.sentences:
            yield sentence


# this creates larger "blotches" of noise which look
# more realistic than just adding gaussian noise
# assumes greyscale with pixels ranging from 0 to 1

def speckle(img):
    severity = np.random.uniform(0, 0.6)
    blur = ndimage.gaussian_filter(np.random.randn(*img.shape) * severity, 1)
    img_speck = (img + blur)
    img_speck[img_speck > 1] = 1
    img_speck[img_speck <= 0] = 0
    return img_speck


sentenceReader = SentenceReader()

for sentence in sentenceReader.sentence_generator():
    if sentence.get_num_words() == 1 and len(sentence.get_text()) in range(2, 4) and \
                    sentence.get_image_height() <= 100 and sentence.get_image_width() <= 280:
        sentence.get_image_data(120, 300)
        print("reached")
