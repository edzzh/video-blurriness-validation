#!/usr/bin/env python3

import sys
import argparse
import os, shutil
import numpy as np
import cv2
from imutils import paths
import statistics
print(cv2.__version__)

def extractImages(pathIn, pathOut):
  vidcap = cv2.VideoCapture(pathIn)
  ret,image = vidcap.read()
  output_dir = os.path.abspath(pathOut)
  ret = True

  # Check if the provided directory exists and is empty
  # if not, then delete exisitng images from the folder
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  else:
    if len(os.listdir(output_dir)) != 0:
      print("Image Folder is not empty!")

      for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)

        try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
          elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        except Exception as e:
          print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
      print("Folder is empty!")

  # Extract images from the provided video for every frame per second
  if vidcap.isOpened():
    currentFrame = 0

    while ret:
      vidcap.set(cv2.CAP_PROP_POS_MSEC,(currentFrame*1000))
      ret,image = vidcap.read()

      if ret:
        image_name = "/frame%d.jpg" % currentFrame

        print('Read a new frame: ', ret)

        cv2.imwrite(output_dir + image_name, image)
      
      currentFrame += 1

def getTestAreaFromImage(pathOut):
  image_output_dir = os.path.abspath(pathOut)
  cropped_image_dir = os.path.abspath(".") + "/cropped_images"

  if not os.path.exists(cropped_image_dir):
    os.makedirs(cropped_image_dir)
  else:
    if len(os.listdir(cropped_image_dir)) != 0:
      print("Cropped Image Folder is not empty!")

      for filename in os.listdir(cropped_image_dir):
        file_path = os.path.join(cropped_image_dir, filename)

        try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
          elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        except Exception as e:
          print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
      print("Folder is empty!")

  if len(os.listdir(image_output_dir)) != 0:
    imagesArr = os.listdir(image_output_dir)
    count = 0

    for singleImage in imagesArr:
      img = cv2.imread(image_output_dir + "/" + singleImage)
      croppedImg = img[0:720, 500:1200]
      imgName = "/test_area%s.jpg" % count
      cv2.imwrite(os.path.abspath("cropped_images") + imgName, croppedImg)
      print("Cropped Image: " + imgName[1:])
      count += 1
  else:
    print("Folder doesn't contain any files to use...")

def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()

def validateBlurriness():
  every_image_laplacian_score = []

  for images in paths.list_images(os.path.abspath("cropped_images")):
    image = cv2.imread(images)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    every_image_laplacian_score.append(fm)
  
  laplacianMedian = statistics.median(every_image_laplacian_score)
  print(laplacianMedian)

  with open('blurriness_median.txt', 'w') as f:
    f.write(str(laplacianMedian))

  if laplacianMedian < 400 and laplacianMedian > 200:
    print("Blurriness is in the acceptable range!")
  elif laplacianMedian < 200:
    print("Blurriness score is below the acceptable range!")
  elif laplacianMedian > 400:
    print("Blurriness score is over the acceptable range!")

if __name__=="__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--pathIn", help="path to video")
    a.add_argument("--pathOut", help="path to images")
    args = a.parse_args()

    if os.path.exists(os.path.abspath(args.pathIn)):
      extractImages(args.pathIn, args.pathOut)
      getTestAreaFromImage(args.pathOut)
      validateBlurriness()
    else:
      print("Can't find the provided video file: " + args.pathIn)