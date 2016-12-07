import glob
import os
import re
import xml.etree.ElementTree as ET
from random import shuffle

import cairocffi as cairo
import numpy as np
from keras.preprocessing import image
from scipy import ndimage
from scipy.misc import imread


class Sentence(object):
    def __init__(self, text, id, file_prefix='sentences'):
        self.text = text
        self.id = id
        self.file_prefix = file_prefix

    def get_text(self):
        return re.sub(r'[^a-zA-Z ]', '', self.text)

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

        if max_shift_y > 0:
            top_pad = np.random.randint(0, int(max_shift_y))
        else:
            top_pad = 0
        bottom_pad = height - (top_pad + image_height)

        if max_shift_x > 0:
            left_pad = np.random.randint(0, int(max_shift_x))
        else:
            left_pad = 0
        right_pad = width - (left_pad + image_width)

        a = np.pad(a, ((top_pad, bottom_pad), (left_pad, right_pad)), 'constant', constant_values=255)

        a = a.astype(np.float32) / 255

        a = np.expand_dims(a, 0)
        a = speckle(a)

        a = image.random_rotation(a, 3 * (width - left_pad) / width + 1)

        return a

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
        files = glob.glob("data/xml/*.xml")
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