import pickle
from typing import Tuple

import torch
from PIL import Image
import numpy as np
from spacy import vocab, tokenizer

from torch.utils.data import Dataset

from fastai1.fastai.core import BatchSamples, random


def numericalize_tokens(tok):
    return np.array([vocab.numericalize(q) + [1] for q in tok])


def build_data(fns_caps, PATH, name):
    filenames, captions = zip(*fns_caps)
    filenames = list(
        map(lambda x: "/content/drive/My Drive/App/Flickr_Data/Images_30k/flickr30k_images/flickr30k_images" + "/" + x,
            filenames))
    captions_tok = list()
    print(len(captions))
    i = 0
    for c in captions:
        i = i + 1
        print(i)
        captions_tok.append(numericalize_tokens(tokenizer.process_all(c)))
    dataset = (filenames, captions_tok)
    pickle.dump(dataset, open(str(PATH) + "/" + name + ".pkl", 'wb'))


def build_art_data(fns_caps, PATH, name):
    filenames, captions = zip(*fns_caps)
    filenames = list(map(lambda x: "/content/drive/My Drive/App/Art_Dataset" + "/" + x, filenames))
    captions_tok = list()
    print(len(captions))
    i = 0
    for c in captions:
        i = i + 1
        print(i)
        captions_tok.append(numericalize_tokens(tokenizer.process_all(c)))
    dataset = (filenames, captions_tok)
    pickle.dump(dataset, open(str(PATH) + "/" + name + "_art.pkl", 'wb'))


class ImageCaptionDataset(Dataset):
    def __init__(self, data, transform=None):
        """
        Args:
          data (tuple): Contains a list of filenames and a list of tokenized and numericalized captions
          transforms (callable, optional): Optional transforms to be applied
        """
        self.filenames = data[0]
        self.captions = data[1]
        self.transform = transform
        self.mult_captions_per_image = not isinstance(data[1][0][0], int)

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        # Grayscale images in dataset have to be onverted as tensor shapes have to match except in dim=0
        image = Image.open(self.filenames[idx]).convert('RGB')
        if self.mult_captions_per_image:
            caption = self.captions[idx][random.randint(0, len(self.captions[idx]) - 1)]
        else:
            caption = self.captions[idx]

        if self.transform is not None:
            image = self.transform(image)

        return (image, caption)


def pad_collate_ImgCap(samples: BatchSamples, pad_idx: int = 1, pad_first: bool = True, backwards: bool = False,
                       transpose: bool = False) -> Tuple[torch.LongTensor, torch.LongTensor]:
    "Function that collect samples and adds padding. Flips token order if needed"
    images, captions = zip(*samples)
    max_len_cap = max([len(c) for c in captions])

    res_cap = torch.zeros(len(samples), max_len_cap).long() + pad_idx

    if backwards: pad_first = not pad_first
    for i, c in enumerate(captions):
        if pad_first:
            res_cap[i, -len(c):] = torch.LongTensor(c)
        else:
            res_cap[i, :len(c)] = torch.LongTensor(c)

    # if backwards:
    #      cap = cap.flip(1)
    if transpose:
        res_cap.transpose_(0, 1)

    return (torch.stack(images, 0, out=None), res_cap), res_cap