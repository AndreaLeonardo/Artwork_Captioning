from functools import partial

from spacy import vocab

from Data import SortSampler, SortishSampler

import Transforms
from BeamSearch import BeamSearch
from ImageCaptionGenerator import ImageCaptionGenerator
from ImageCaptionGenerator import ImageCaptionLoss
from ImageCaptionDataset import ImageCaptionDataset, pad_collate_ImgCap
from BleuMetric import BleuMetric
import torch

from Utils import visualize_attention
from fastai1.fastai.basic_data import DataBunch, DataLoader
from fastai1.fastai.basic_train import Learner


from PIL import Image
from pathlib import Path
import pickle

from fastai1.fastai.torch_core import to_device


class ImageCaptionLearner():

    def __init__(self):

        self.vocab = pickle.load(open("pickle/vocab.pkl", 'rb'))
        self.art_vocab = pickle.load(Path("pickle/art_vocab.pkl").open('rb'))

        self.valid_data = pickle.load(Path("pickle/valid.pkl").open('rb'))
        self.test_data = pickle.load(Path("pickle/test.pkl").open('rb'))
        self.train_data = pickle.load(Path("pickle/train.pkl").open('rb'))

        self.art_valid_data = pickle.load(Path("pickle/art_valid.pkl").open('rb'))
        # art_test_data  = pickle.load((PATH/"art_test.pkl").open('rb'))
        self.art_train_data = pickle.load(Path("pickle/art_train.pkl").open('rb'))

        self.valid_dataset = ImageCaptionDataset(self.valid_data, transform=Transforms.valid_tfms)
        self.train_dataset = ImageCaptionDataset(self.train_data, transform=Transforms.valid_tfms)

        self.art_valid_dataset = ImageCaptionDataset(self.art_valid_data, transform=Transforms.valid_tfms)
        self.art_train_dataset = ImageCaptionDataset(self.art_train_data, transform=Transforms.train_tfms)

        bs = 80
        art_bs = 50
        self.imgcap_collate_func = partial(pad_collate_ImgCap, pad_first=False, transpose=True)

        self.val_sampler = SortSampler(self.valid_data[1], key=lambda x: len(self.valid_data[1][x]))
        self.trn_sampler = SortishSampler(self.train_data[1], key=lambda x: len(self.train_data[1][x]), bs=bs)
        self.art_val_sampler = SortSampler(self.art_valid_data[1], key=lambda x: len(self.art_valid_data[1][x]))
        self.art_trn_sampler = SortishSampler(self.art_train_data[1], key=lambda x: len(self.art_train_data[1][x]), bs=art_bs)

        self.val_dl = DataLoader(dataset=self.valid_dataset, batch_size=bs, sampler=self.val_sampler, collate_fn=self.imgcap_collate_func)
        self.trn_dl = DataLoader(dataset=self.train_dataset, batch_size=bs, sampler=self.trn_sampler, collate_fn=self.imgcap_collate_func)
        self.art_val_dl = DataLoader(dataset=self.art_valid_dataset, batch_size=art_bs, sampler=self.art_val_sampler,
                                collate_fn=self.imgcap_collate_func)
        self.art_trn_dl = DataLoader(dataset=self.art_train_dataset, batch_size=art_bs, sampler=self.art_trn_sampler,
                                collate_fn=self.imgcap_collate_func)



        self.n_layers, self.emb_sz = 1, 500
        gpu = torch.device('cpu')

        self.imgCapGen = ImageCaptionGenerator(gpu, 7, 2048, len(self.vocab.itos), self.emb_sz, 50, self.n_layers, p_drop=0.2)
        self.opt_fn = partial(torch.optim.Adam, betas=(0.8, 0.99))
        self.dataBunch = DataBunch(train_dl=self.trn_dl, valid_dl=self.val_dl, device=gpu, path=Path(""), collate_fn=self.imgcap_collate_func)
        self.art_dataBunch = DataBunch(train_dl=self.art_trn_dl, valid_dl=self.art_val_dl, device=gpu, path=Path(""),
                                  collate_fn=self.imgcap_collate_func)
        self.learn = Learner(data=self.dataBunch, model=to_device(self.imgCapGen, gpu), opt_func=self.opt_fn, loss_func=ImageCaptionLoss, metrics=[BleuMetric()])
        print("Learner initialized!")

    def load(self, path):
        self.learn.load(path)

    def predict(self, path, beam_width):

        beam_search = BeamSearch(self.learn.model.encode, self.learn.model.decode_step, beam_width)

        image = Transforms.valid_tfms(Image.open(path).convert('RGB'))
        results = beam_search(image)
        dictionary = {
            "caption": self.vocab.textify(results[0]),
            "beam_width": beam_width
        }

        return self.vocab.textify(results[0])

