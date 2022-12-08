#######################################################################################
# this script is for unpacking files from .dat archives                               #
# Original Author: erik945 (https://forum.xentax.com/viewtopic.php?p=110862#p110862)  #
# Modified by: Sebi | hrkrx (FA Emu)                                                  #
#######################################################################################
from logging import getLogger
import struct
import os

# unpacks the given file to the given directory
def unpack_file(unpack_file, target_directory):
    local_log = getLogger()
    
    local_log.info("Directory -> "+target_directory)

    r_bytes = [0, 0, 0, 0, 0, 0, 0, 0]
    r_bytes_l = [0xDD, 0x88, 0x55, 0x22, 0x14, 0, 0, 0]

    dat_file = open(unpack_file, 'rb')

    dat_file.seek(0, os.SEEK_END)
    dat_file_size = dat_file.tell()
    dat_file.seek(0, os.SEEK_SET)

    file_name = ""
    previouse_offset = 0

    local_log.info("dat_file_size -> " + str(dat_file_size))

    while (dat_file.tell() < dat_file_size):

        if (r_bytes == r_bytes_l):
            back_offset = dat_file.tell()
            dat_file.seek(0x12, os.SEEK_CUR)
            file_name_size = struct.unpack('I', dat_file.read(4))[0]
            if (file_name_size < 0xFF):
                if (file_name != ""):
                    back_offset2 = dat_file.tell()
                    (dirName, fileName) = os.path.split(
                        target_directory + file_name.decode('ascii'))
                    if ((os.path.exists(dirName)) == False):
                        os.makedirs(dirName)
                    file_size = back_offset - 8 - previouse_offset
                    dat_file.seek(previouse_offset, os.SEEK_SET)
                    byte_data = dat_file.read(file_size)
                    Ufile = open(
                        (target_directory + file_name.decode('ascii')), 'wb')
                    Ufile.write(byte_data)
                    Ufile.close()
                    dat_file.seek(back_offset2, os.SEEK_SET)
                file_name = dat_file.read(file_name_size)
                local_log.info("File discriptor offset -> " +
                      str(back_offset - 8) + " " + file_name.decode('ascii'))
                previouse_offset = dat_file.tell()
                r_bytes = [0, 0, 0, 0, 0, 0, 0, 0]
            else:
                dat_file.seek(back_offset, os.SEEK_SET)
        else:
            i = 0
            while (i < 7):
                r_bytes[i] = r_bytes[i+1]
                i += 1
            r_bytes[7] = file_name_size = struct.unpack(
                'B', dat_file.read(1))[0]
        # print(r_bytes)

    back_offset = dat_file.tell()
    (dirName, fileName) = os.path.split(
        target_directory + file_name.decode('ascii'))
    if ((os.path.exists(dirName)) == False):
        os.makedirs(dirName)
    file_size = back_offset - previouse_offset
    dat_file.seek(previouse_offset, os.SEEK_SET)
    byte_data = dat_file.read(file_size)
    Ufile = open(target_directory + file_name.decode('ascii'), 'wb')
    Ufile.write(byte_data)
    Ufile.close()

# recursively searches for all .dds or .DDS files in the given directory
# exclude _C.dds files as they are not worth upscaling 
def collect_dds_files (path):
    dds_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".dds") or file.endswith(".DDS"):
                if not file.endswith("_C.dds"):
                    dds_files.append(os.path.join(root, file))
    return dds_files

if __name__ == '__main__':
    unpack_file("D:\\Programs\\FA\\2094209\\Data\\map.dat",
                "D:\\Programs\\FA\\2094209\\Data\\")
