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

class EVIFile():
    """
        A class for handling XCounter EVI file format; 
        Follow the naming convention of the ImageJ Java plugin
    """
    headers = {} # Dictionary for EVI headers
    data = [] # Image data
    width = 0
    height = 0
    nImages = 0 # how many frames in one scan
    intelByteOrder = True
    tds = False
    tdsTruncate = False
    TE = True 
    TC = 1
    numberOfBoards = 1
    numberOfRows = 1
    sequenceHeaderBytes = 0 
    frameHeaderBytes = 0
    is32bit = False

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
        
        for i in range(0, 76): # 76 lines of file header
            line = fp.readline()
            name, var = line.partition(" ")[::2]
            self.headers[name.strip()] = var

        image_type   = self.headers["Image_Type"]
        self.is32bit = (image_type == "Single") or (image_type == "32-bit Real")
        self.width   = int(self.headers["Width"])
        self.height  = int(self.headers["Height"])
        self.nImages = int(self.headers["Scan_Frame_Count"]) # what is difference from Nr_of_images?
        self.frameHeaderBytes = int(self.headers["Gap_between_iamges_in_bytes"])
        self.intelByteOrder = self.headers["Endianness"] == "Little-endian byte order"
        self.TC = int(self.headers["HV_TC"])
        self.sequenceHeaderBytes = int(self.headers["Offset_To_First_Image"])
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

        self.data = np.zeros((self.height, self.width, self.nImages),dtype=np.uint16)

        fp.seek(0) # go back to the begining of the file
        fp.read(self.sequenceHeaderBytes-self.frameHeaderBytes) #skip file header
        for i in range(0, self.nImages):
            fp.read(self.frameHeaderBytes) # skip frame header, can be multiple frames
            if self.is32bit:
                tmp = np.fromfile(fp,dtype=np.uint32,count=self.width*self.height).astype(np.uint16)
            else:
                tmp = np.fromfile(fp,dtype=np.uint16,count=self.width*self.height)
            self.data[:,:,i] = np.reshape(tmp, (self.height, self.width))
        fp.close()


    def print_header(self):
        "Print the full header of the EVI file"
        for i in self.headers:
            print("{}:{}".format(i, self.headers[i]))

    def show(self):
        "Show the EVI image"
        for i in range(0, self.nImages):
            plt.figure(i)
            plt.imshow(self.data[:,:,i], cmap='gray')
            plt.show(block=True)

    def get_data(self):
        "Return the numpy arrage of the raw data"
        return self.data

    def get_header(self):
        "Return the header dictionary"
        return self.headers

    def shape(self):
        "Show the dimension of the image"
        print("(H, W, frames) = ", [self.height, self.width, self.nImages])
        return [self.height, self.width, self.nImages]


def EVIread(filename):
    "Utility function to read the EVI data and header directly"
    evi = EVIFile(filename)
    return evi.get_data(), evi.get_header()


if __name__ == '__main__':
    filename = '/Users/wangzhentian/Desktop/test1_TE.EVI'
    # approach 1
    # fEVI = EVIFile()
    # fEVI.read(filename)

    # approach 2
    fEVI = EVIFile(filename)
    fEVI.print_header()
    fEVI.shape()
    #fEVI.show()
    data = fEVI.get_data()
    plt.figure()
    plt.imshow(data[:,:,1],cmap='gray') # show the first frame
    plt.show(block=True)

    # approach 3
    # data, headers = EVIread(filename)
    # plt.figure()
    # plt.imshow(data[:,:,1],cmap='gray') # show the first frame
    # plt.show(block=True)
    