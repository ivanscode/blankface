# coding: utf-8

import sys, os, argparse
#import face_alignment
from skimage import io
import skimage.transform as st
from skimage.restoration import inpaint
from api import PRN
import numpy as np
from glob import glob
import scipy.io as sio
import scipy.ndimage as ni
from time import time
from utils.write import write_obj_with_colors
from utils.rotate_vertices import frontalize

def saveImage(image, path, folder):
    name = path.strip().split('/')[-1][:-4]
    io.imsave(os.path.join(folder, name + '.jpg'), image)

def flatten(image, list, colors, w, h):
    '''
    Match corresponding vertices and color data to an image

    Returns an image
    '''
    for i in range(0, list[:, 0].size):
        x = min(max(0, int(round(list[i, 1]))), h - 1)
        y = min(max(0, int(round(list[i, 0]))), w - 1)
        image[x, y] = colors[i]

        #Fill in the black gaps due to rounding
        image[max(x - 1, 0), y] = colors[i]
        image[x, max(y - 1, 0)] = colors[i]
        image[min(x + 1, h - 1), y] = colors[i]
        image[x, min(y + 1, w - 1)] = colors[i]
    
    return image

def findMask(image, mode=''):
    '''
    First iteration of artifact finder. Finds all points in image that are dark,
    in the case of a face flatten from a 3D model, there will be blanks that
    need to be filled in

    Modes:
        Radial - only searches in a circular area of image based off the center
        Full/None - searches through the entire image

    Returns a mask containing these areas
    '''

    [h, w, _] = image.shape
    mask = np.zeros(image.shape[:-1])
    cx = w / 2; cy = h / 2
    rs = (cx - cx / 12)**2
    for i in range(0, h):
        for j in range(0, w):
            [r, g, b] = image[i, j]
            if(mode == 'radial'):
                dx = j - cx
                dy = i - cy
                ds = dx**2 + dy**2
                if(ds <= rs):
                    if(r < 30):
                        mask[i, j] = 1
            else:  
                if(r < 30):
                    mask[i, j] = 1

    return mask

def getExtremes(list):
    '''
    Get bounding box of vertices (frontalized or otherwise)

    Returns left, right, top, bottom
    '''

    return np.min(list[:, [0]]), np.max(list[:, [0]]), np.min(list[:, [1]]), np.max(list[:, [1]])

def fixBounds(list):
    '''
    Shift vertices to (0, 0) for image processing

    Returns the shifted vertices and the new extremes
    '''
    minx, maxx, miny, maxy = getExtremes(list)

    list[:, [0]] += 0 - minx
    maxx += 0 - minx

    list[:, [1]] += 0 - miny
    maxy += 0 - miny

    return list, int(round(maxx)), int(round(maxy))

def printProgress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    '''
    Terminal progress bar

    Source: https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
    '''
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def parse_args():
    parser = argparse.ArgumentParser(description='Face frontalization v1.0')
    parser.add_argument('--face', dest='face', help='Output frontalized face onto original image', default=False, type=bool)
    parser.add_argument('--fill', dest='fill', help='Amount of smoothing for black gaps', default=2, type=int)
    parser.add_argument('--save', dest='save', help='Save directory for output files', default='Images/results_temp', type=str)
    parser.add_argument('--td', dest='td', help='Save 3D model to obj file', default=False, type=bool)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()

    os.environ['CUDA_VISIBLE_DEVICES'] = '0' # GPU number, -1 for CPU
    prn = PRN(is_dlib = True) 

    image_folder = 'Images/lfw'
    save_folder = args.save
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    types = ('*/*.jpg', '*/*.png')
    image_path_list= []
    for files in types:
        image_path_list.extend(glob(os.path.join(image_folder, files)))
    total_num = len(image_path_list)

    printProgress(0, total_num, suffix='Complete', bar_length=50)

    # ----- THE MEAT ------

    for i, image_path in enumerate(image_path_list):
        image = io.imread(image_path)

        pos = prn.process(image) #Run through net
        vertices = prn.get_vertices(pos) #Converted to list (n x 3) with relevant points only
        frontalized = frontalize(vertices) #Face the camera
        colors = prn.get_colors(image, vertices) #Texture map

        if args.td:
            frontalized, w, h = fixBounds(frontalized)
            name = image_path.strip().split('/')[-1][:-4]
            frontalized[:,1] = h - 1 - frontalized[:,1]
            write_obj_with_colors(os.path.join(save_folder, name + '.obj'), frontalized, prn.triangles, colors)
        else:
            if args.face:   
                [h, w, _] = image.shape #Copy original image specs
                l = int(round(min(vertices[:, [0]]))); r = int(round(max(vertices[:, [0]])))
                t = int(round(min(vertices[:, [1]]))); b = int(round(max(vertices[:, [1]])))

                frontalized, w, h = fixBounds(frontalized)
                new_image = np.zeros([h, w, 3], dtype=np.uint8)             
                
                #Assign RGB values to new image
                new_image = flatten(new_image, frontalized, colors, w, h)

                #Fix holes in image
                mask = findMask(new_image, mode='radial')
                new_image = inpaint.inpaint_biharmonic(new_image, mask, multichannel=True) 

                #scale to match head
                new_image = st.resize(new_image, (b - t, r - l), anti_aliasing=True, mode='constant')
                new_image = 255 * new_image
                new_image = new_image.astype(np.uint8)

                #Paste face onto image and save
                old_image = image.copy()
                old_image[t:t+(b - t), l:l+(r - l)] = new_image
                mask_ind = (old_image == 0)
                old_image[mask_ind] = image[mask_ind]

                saveImage(old_image, image_path, save_folder)     
            else:
                #Shift list into new image box
                frontalized, w, h = fixBounds(frontalized)
                new_image = np.zeros([h, w, 3], dtype=np.uint8)             
                
                #Assign RGB values to new image
                new_image = flatten(new_image, frontalized, colors, w, h)

                #Fill in holes and save
                mask = findMask(new_image, mode='radial')
                new_image = inpaint.inpaint_biharmonic(new_image, mask, multichannel=True)
                new_image = 255 * new_image
                new_image = new_image.astype(np.uint8)

                saveImage(new_image, image_path, save_folder)
        
        printProgress(i + 1, total_num, suffix='Complete', bar_length=50)