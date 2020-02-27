# coding=utf-8
from PIL import Image
import numpy as np
import threading
import os
from PySide2 import QtCore
from PySide2 import QtWidgets
import sys

np.set_printoptions(threshold=np.inf)

class ModuloError(Exception):
    def __init__(self,value1,value2):
        self.value1 = value1
        self.value2 = value2
    def __str__(self):
        return str("Unable to mod " + str(self.value1) + " with file counts of "+str(self.value2))

class PictureSizeError(Exception):
    pass

def allFactor(n):
    if n == 0: return [0]
    if n == 1: return [1]
    return [x for x in range(1,n//2+1) if n%x == 0]

def intOnlyModulo(files,row):
    if(len(files) % row != 0):
        raise ModuloError(row,len(files))
    else:
        return len(files) / row

def LoadFiles(pathFromUI):
    directory = "src" 
    path = os.getcwd() +"\\"+directory if pathFromUI =="" else pathFromUI
    srcpath = os.walk(path)
    filePaths = [path +"\\"+file for path, dir_list, file_list in srcpath for file in file_list]
    return filePaths

def createArray(filePaths, rowsFromUI):
    rows = rowsFromUI
    line = 1
    try:
        line = int(intOnlyModulo(filePaths,rows))
    except ModuloError as e:
        print(e)
    firstPic = Image.open(filePaths[0])
    finalArray = np.zeros([firstPic.size[0]*rows, firstPic.size[1]*line, 4], dtype=int)
    return finalArray,rows,line

class PicSealInstance:
    def __init__(self,infoTuple,filePaths):
        self.finalArray = infoTuple[0]
        self.tileSize = (infoTuple[1],infoTuple[2])
        self.finalArrayLock = threading.Lock()
        self.filePaths = filePaths
        self.threads = []
        self.pictureNumber = infoTuple[1]*infoTuple[2]

    def startExecuteThreads(self):
        #print("startSeal")
        for i in range(0,self.pictureNumber):
            currentThread = threading.Thread(target=self.writeArray, args=(i,self.tileSize))
            currentThread.start()
            self.threads.append(currentThread)
        for thread in self.threads:
            thread.join()
        self.finalImage = Image.fromarray(np.uint8(self.finalArray))

    def writeArray(self,i,tileSize):
        currPictureArray =np.array(Image.open(self.filePaths[i]))
        picSize = currPictureArray.shape
        x = 0
        y = 0
        if(i!=0):
            x = i // tileSize[1] # 所在行，对应最终拼贴的0
            y = i % tileSize[1] # 所在列，对应最终拼贴的1

    # 计算当前图片上方和下方应该填充的空像素量
        XUP = x * picSize[0]
        XDOWN = (tileSize[0] - (x + 1)) * picSize[0]
        YLEFT = y * picSize[1]
        YRIGHT =  (tileSize[1] - (y+1)) * picSize[1]
        currPictureArray = np.pad(currPictureArray, ((XUP,XDOWN),(YLEFT,YRIGHT),(0,0)),'constant')
        self.finalArrayLock.acquire()
        self.finalArray = self.finalArray + currPictureArray
        self.finalArrayLock.release()
        #print("SubThread" + str(i))

    #由前端调用的保存文件
    def saveCurrentFile(self,finalFilePath):
        self.finalImage.save(finalFilePath)