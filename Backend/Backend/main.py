from PIL import ImageFile

from ImageCaptionLearner import ImageCaptionLearner
ImageFile.LOAD_TRUNCATED_IMAGES = True





if __name__ == '__main__':
    imgCaptLrn = ImageCaptionLearner()
    imgCaptLrn.load("bestmodel_30k")
    print(imgCaptLrn.predict("images/pipol.jpeg", 10))
