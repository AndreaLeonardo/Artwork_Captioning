from torchvision import transforms
from torchvision.transforms import functional

sz=224

train_tfms = transforms.Compose([
    transforms.RandomResizedCrop(sz, scale=(0.2,1.0)),
    # transforms.Resize(sz),
    transforms.RandomRotation(10, expand=False),
    # transforms.CenterCrop(sz),
    # transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ToTensor(),
    transforms.Normalize([0.5238, 0.5003, 0.4718], [0.3159, 0.3091, 0.3216])
])

valid_tfms = transforms.Compose([
    transforms.Resize(sz),
    transforms.CenterCrop(sz),
    transforms.ToTensor(),
    transforms.Normalize([0.5238, 0.5003, 0.4718], [0.3159, 0.3091, 0.3216])
])

inv_normalize = transforms.Normalize(
    mean=[-0.5238/0.3159, -0.5003/0.3091, -0.4718/0.3216],
    std=[1/0.3159, 1/0.3091, 1/0.3216]
)


denorm = transforms.Compose([
    inv_normalize,
    transforms.functional.to_pil_image
])
