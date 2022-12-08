import os
import time
import argparse
from PIL import Image
import tensorflow as tf
import tensorflow_hub as hub

#####################
#     Constants     #
#####################

# ESRGAN model
ESRGAN_MODEL_PATH = "https://tfhub.dev/captain-pool/esrgan-tf2/1"

# convert jpg to png
def jpg_to_png(jpg_file, png_file):
    img = Image.open(jpg_file)
    img.save(png_file)

# generate a alphamask from the alpha values of a png file
def generate_alphamask(png_file, alphamask_file):
    img = Image.open(png_file)
    img = img.convert('RGBA')
    datas = img.getdata()
    newData = []
    for item in datas:
        newData.append((item[3], item[3], item[3], 255))
    img.putdata(newData)
    img.save(alphamask_file)

# apply an alphamask to a png file
def apply_alphamask(png_file, alphamask_file, output_file):
    img = Image.open(png_file)
    img = img.convert('RGBA')
    datas = img.getdata()
    newData = []
    mask = Image.open(alphamask_file)
    mask = mask.convert('RGBA')
    mask = mask.getdata()
    for i in range(len(datas)):
        newData.append((datas[i][0], datas[i][1], datas[i][2], mask[i][0]))
    img.putdata(newData)
    img.save(output_file)

# remove alpha channel from a png file (white background)
def remove_alpha_channel(png_file, output_file):
    img = Image.open(png_file)
    img = img.convert('RGBA')
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[3] == 0:
            newData.append((255, 255, 255, 255))
        else:
            newData.append((item[0], item[1], item[2], 255))
    img.putdata(newData)
    img.save(output_file)

def preprocess_image(image_path):
  """ Loads image from path and preprocesses to make it model ready
      Args:
        image_path: Path to the image file
  """
  hr_image = tf.image.decode_image(tf.io.read_file(image_path))
  # If PNG, remove the alpha channel. The model only supports
  # images with 3 color channels.
  if hr_image.shape[-1] == 4:
    hr_image = hr_image[...,:-1]
  hr_size = (tf.convert_to_tensor(hr_image.shape[:-1]) // 4) * 4
  hr_image = tf.image.crop_to_bounding_box(hr_image, 0, 0, hr_size[0], hr_size[1])
  hr_image = tf.cast(hr_image, tf.float32)
  return tf.expand_dims(hr_image, 0)

def save_image(image, filename):
  """
    Saves unscaled Tensor Images.
    Args:
      image: 3D image tensor. [height, width, channels]
      filename: Name of the file to save.
  """
  if not isinstance(image, Image.Image):
    image = tf.clip_by_value(image, 0, 255)
    image = Image.fromarray(tf.cast(image, tf.uint8).numpy())
  image.save("%s.jpg" % filename)
  print("Saved as %s.jpg" % filename)

def download_esrgan_model():
  """
    Downloads the ESRGAN model from TFHub.
  """
  return hub.load(ESRGAN_MODEL_PATH)

def upscale_image(model, image_path, downscale_if_needed=True):
  """
    Upscales an image using the ESRGAN model.
    Args:
      model: The ESRGAN model.
      image_path: Path to the image to be upscaled.
  """
  if downscale_if_needed:
    # Downscale the image if it's too big.
    # The model only supports images up to 2048x2048.
    image = Image.open(image_path)
    if image.size[0] > 2048:
      # scale to 2048 and calculate new height
      scale = 2048 / image.size[0]
      new_height = int(image.size[1] * scale)
      image = image.resize((2048, new_height), Image.ANTIALIAS)
      image.save(image_path)

    if image.size[1] > 2048:
      # scale to 2048 and calculate new width
      scale = 2048 / image.size[1]
      new_width = int(image.size[0] * scale)
      image = image.resize((new_width, 2048), Image.ANTIALIAS)
      image.save(image_path)

  hr_image = preprocess_image(image_path)
  sr_image = model(hr_image)
  return sr_image[0]

if __name__ == "__main__":
  # parameters: model_path, input_file, output_file
  # setup argparser
  parser = argparse.ArgumentParser(description='Upscale a png file using ESRGAN.')
  parser.add_argument("-i", '--input_files', type=str, help='input file', required=True)
  parser.add_argument("-o", '--output_file', type=str, help='output file', required=False, default=None)
  parser.add_argument("-m", '--model_path', type=str, help='path to the ESRGAN model')

  # parse arguments
  args = parser.parse_args()
  model_path = args.model_path
  input_files = str.split(args.input_files, ',')
  output_file = args.output_file

  # load model from file
  print("Loading model...")
  # check if model is present in the specified path
  if not os.path.exists(model_path):
    print("Model not found in specified path. Downloading...")

  model = tf.saved_model.load(model_path)
  print("Model loaded.")

  for image in input_files:
    # upscale image
    print("Upscaling image...")
    start_time = time.time()
    sr_image = upscale_image(model, image)
    print("Image upscaling complete. Took %s seconds." % (time.time() - start_time))

    # save image
    print("Saving image...")
    if output_file is None:
      output_file = os.path.basename(image)[:-4] + "_upscaled"
      save_image(sr_image, output_file)
    print("Image saved.")