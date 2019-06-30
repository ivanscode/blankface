# blankface
Convert profile images to 160 x 160 renders of 3d vertices of the face with a blank texture

There are 3 stages to the process

1. front - Convert profile image to obj file with vertices sourced from https://github.com/YadiraF/PRNet
2. render - Render vertices to jpg
3. crop (optional) - Crop image to 160x160 cutting out useless borders

## Dependencies
Note: some are not lsited

TensorFlow is required for obj conversion as well as the training file used 
https://github.com/YadiraF/PRNet - for full list of dependecies

render is written completely in Matlab

crop uses numpy and skimage as the primary libraries for image manipulation