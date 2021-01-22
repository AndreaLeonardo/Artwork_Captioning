# Artwork_Captioning

This project aims to describe cultural works, through the image captioning. The main objective is not only to generate descriptive captions of a specific area, such as the cultural one, but the project also aims at understanding what are the logical mechanics that man applies in the description of specific images or photographs and how a neaural network can emulate its reasoning.

## Describe an Image

Describing an image is certainly not a simple thing and the task is even more difficult if the subject of the description is a work of art.
The purpose of this project is therefore relatively less demanding than a true description of an image. However, it will be essential to distinguish a statue from a painting, a man from a woman, a young man from an elderly person and it would be interesting to describe in as much detail as possible the gestures and clothes of the subjects, the background decorations and the emotions of the faces.

## Application
we have designed an application that takes a photograph and shows you a description of it. Its use is very simple as you can see from the images below:

- inserimento dell'URL
<img src="/demo/inserimento_url.png" width="400">

- scatto della fotografia
<img src="/demo/scatto_foto.png" width="300">

## Implementation

In this project, an image captioning neural network (https://github.com/fg91/Neural-Image-Caption-Generation-Tutorial) was used, retrained, initially with a photographic dataset (Flickr30k) and subsequently with a dedicated dataset created by me.

### Frontend
The frontend side was implemented with Flutter. To be able to use it, simply import the ''Frontend" folder into an Android Studio project.

### Backend
The frontend side was implemented in Python. The '' Backend "folder contains the code files to be able to test the network and its training locally, but requires the installation of several libraries related to machine learning, including torch and fastai (specifically fasta1, the first version).

In order to use the code faster, just use the notebook directly on Google Colab.
n this case, to generate the url to insert in the application, it will be sufficient to execute the cell following the installation of ngrok. It will generate in output the ngrok tunnel to insert.


