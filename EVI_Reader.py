#!/usr/bin/env python
"""
Created on Tue Dec 11 2018

Class for reading XCounter EVI format

"""
__author__ = "Zhentian Wang"
__copyright__ = "No Copyright"
__credits__ = ["Zhentian Wang"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Zhentian Wang"
__email__ = "wang.zhentian@gmail.com"
__status__ = "Develop"

import matplotlib.pyplot as plt
import numpy as np
import sys

class EVI_Reader():
    """
        A class for handling XCounter EVI file format; 
        Follow the naming convention of the ImageJ Java plugin
    """
    headers = {} # Dictionary for EVI headers
    data = [] # Image data
    width = 0
    height = 0
    offset = 0
    nImages = 0
    gapBetweenImages = 0
    intelByteOrder = True
    tds = False
    tdsTruncate = False
    TE = True 
    numberOfBoards = 1
    numberOfRows = 1

    def __init__(self,filename=""):
        "Initiate with a filename"
        if filename != "":
            self.read(filename)
        else:
            pass

    def read(self, filename):
        "Read the EVI file"
        try:
            fp = open(filename, encoding='latin-1')
        except:
            print("File cannot be found or opened.")
            return
        
        for i in range(0, 76):
            line = fp.readline()
            name, var = line.partition(" ")[::2]
            self.headers[name.strip()] = var

        image_type = self.headers["Image_Type"]
        real = (image_type == "Single") or (image_type == "32-bit Real")
        # here it meant to handle 32bit or 16bit data, but it is 16bit by default now
        self.width = int(self.headers["Width"])
        self.height = int(self.headers["Height"])
        self.offset = int(self.headers["Offset_To_First_Image"])
        self.nImages = int(self.headers["Nr_of_images"])
        self.gapBetweenImages = int(self.headers["Gap_between_iamges_in_bytes"])
        self.intelByteOrder = self.headers["Endianness"] == "Little-endian byte order"
        self.tds = self.headers["Tds"].lower() == "true"
        if "Tds_Truncate_to_015" in self.headers:
            self.tdsTruncate = self.headers["Tds_Truncate_to_015"].lower() == "true"
        else:
            self.TE = self.headers["Energy_type"].lower() == "TOTAL_ENERGY" 
            if self.TE:
                self.tdsTruncate = self.headers["Tds_Truncate_to_015_TE"].lower() == "true"
            else:
                self.tdsTruncate = self.headers["Tds_Truncate_to_015_HE"].lower() == "true"
        if "Number_of_boards" in self.headers:
            self.numberOfBoards = int(self.headers["Number_of_boards"])
        if "Number_of_board_rows" in self.headers:
            self.numberOfRows = int(self.headers["Number_of_board_rows"])
        # Start to read the raw data
        self.data = np.fromfile(fp,dtype=np.uint16,count=self.width*self.height)
        self.data = np.reshape(self.data,(self.height, self.width))
        fp.close()

    def print_header(self):
        "Print the full header of the EVI file"
        for i in self.headers:
            print("{}:{}".format(i, self.headers[i]))

    def show(self):
        "Show the EVI image"
        plt.figure()
        plt.imshow(self.data, cmap='gray')
        plt.show(block=True)

    def get_data(self):
        "Return the numpy arrage of the raw data"
        return self.data

    def shape(self):
        "Show the dimension of the image"
        return [self.height, self.width]


if __name__ == '__main__':
    filename = '/Users/wangzhentian/Desktop/test1_TE.EVI'
    reader = EVI_Reader()
    reader.read(filename)
    reader.print_header()
    #reader.show()
    #print(reader.shape())