from wand import image

def dds_to_png(dds_file, png_file):
    with image.Image(filename=dds_file) as img:
        img.format = 'png'
        img.save(filename=png_file)
        return img.compression

def png_to_dds(png_file, dds_file, compression='dxt5'):
    with image.Image(filename=png_file) as img:
        img.format = 'dds'
        img.compression = compression
        img.save(filename=dds_file)