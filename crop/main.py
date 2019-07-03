import sys, os
from glob import glob
from skimage import io
import skimage.transform as st
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool 

def saveImage(image, path, folder):
    name = path.strip().split('/')[-1][:-4]
    io.imsave(os.path.join(folder, name + '.jpg'), image)

def findTop(image):
    [h, w, _] = image.shape
    for j in range(0, h):
        for k in range(0, w):
            if(image[j, k, 0] != 255 and image[j, k, 1] != 255 and image[j, k, 2] != 255):
                return j

def findLeft(image):
    [h, w, _] = image.shape
    for j in range(0, w):
        for k in range(0, h):
            if(image[k, j, 0] != 255 and image[k, j, 1] != 255 and image[k, j, 2] != 255):
                return j

def findBot(image):
    [h, w, _] = image.shape
    for j in range(h - 1, 0, -1):
        for k in range(0, w):
            if(image[j, k, 0] != 255 and image[j, k, 1] != 255 and image[j, k, 2] != 255):
                return j

def findRight(image):
    [h, w, _] = image.shape
    for j in range(w - 1, 0, -1):
        for k in range(0, h):
            if(image[k, j, 0] != 255 and image[k, j, 1] != 255 and image[k, j, 2] != 255):
                return j

def cropImage(image_path):
    image = io.imread(image_path)

    l = findLeft(image)
    t = findTop(image)
    b = findBot(image)
    r = findRight(image)

    new_image = image[t:b, l:r]

    new_image = st.resize(new_image, (160, 160), anti_aliasing=True, mode='constant')
    new_image = 255 * new_image
    new_image = new_image.astype(np.uint8)

    saveImage(new_image, image_path, save_folder)

image_folder = '/home/ivan/face-frontilization/Images/results_face'
save_folder = '/home/ivan/crop/output'

if not os.path.exists(save_folder):
    os.mkdir(save_folder)


types = ('*.jpg', '*.png')
image_path_list= []
for files in types:
    image_path_list.extend(glob(os.path.join(image_folder, files)))
total_num = len(image_path_list)

pool = ThreadPool(8) 
results = pool.map(cropImage, image_path_list)

#for i, image_path in enumerate(image_path_list):
    



