import xml.etree.cElementTree as ET
import pickle
import cv2.cv2 as cv
import numpy as np
import random
import Config as cfg
import os
import time

PASCAL_VOC_PATH = "./VOCdevkit/"


class PascalVOC:
    def __init__(self):
        # data path
        self.ImagePath = cfg.ImagePath
        self.AnnotationPath = cfg.AnnotationsPath
        # image settings
        self.ImageSize = cfg.ImageSize
        self.CellNum = cfg.CellSize
        self.Classes = cfg.Classes
        self.ClassesDict = cfg.ClassesDict
        # path to save data
        self.SaveTrain = cfg.TrainSavePath
        self.SaveVal = cfg.ValSavePath
        # get image file list
        self.ImageList = os.listdir(self.ImagePath)
        self.ImageList = [i.replace(".jpg", "") for i in self.ImageList]
        random.shuffle(self.ImageList)
        # divide dataset
        self.TrainPercentage = cfg.TrainPercentage
        self.TrainNum = int(len(self.ImageList) * self.TrainPercentage)
        self.ValNum = len(self.ImageList) - self.TrainNum
        self.TrainImageList = self.ImageList[:self.TrainNum]
        self.ValImageList = self.ImageList[self.TrainNum:]

        if os.path.isfile(self.SaveTrain) and os.path.isfile(self.SaveVal):
            self.TrainData = self.__LoadPickle__(self.SaveTrain)
            self.ValData = self.__LoadPickle__(self.SaveVal)
        else:
            # load label
            self.__LoadImageLabel__()
            self.__SaveToPickle__(self.SaveTrain, self.TrainData)
            self.__SaveToPickle__(self.SaveVal, self.ValData)

    @staticmethod
    def __LoadPickle__(file_path):
        print("Load data from: " + file_path)
        with open(file_path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def __SaveToPickle__(file_path, data_to_save):
        print("Save data to: " + file_path)
        with open(file_path, "wb") as f:
            pickle.dump(data_to_save, f)

    def __LoadImageLabel__(self):
        print("Loading labels from: " + self.AnnotationPath)

        self.TrainData = []
        # load train dataset
        for TrainImage in self.TrainImageList:
            Label, NumObject = self.__LoadLabel__(TrainImage)
            if NumObject == 0:
                continue
            image_path = os.path.join(self.ImagePath, TrainImage + ".jpg")
            self.TrainData.append({"ImagePath": image_path, "Label": Label})
        self.ValData = []
        # load val dataset
        for ValImage in self.ValImageList:
            Label, NumObject = self.__LoadLabel__(ValImage)
            if NumObject == 0:
                continue
            image_path = os.path.join(self.ImagePath, ValImage + ".jpg")
            self.ValData.append({"ImagePath": image_path, "Label": Label})

    def __LoadLabel__(self, image_name):
        AnnotationPath = os.path.join(self.AnnotationPath, image_name + ".xml")

        label = np.zeros((self.CellNum, self.CellNum, 6))

        XMLTree = ET.parse(AnnotationPath)
        Objects = XMLTree.findall("object")

        Size = XMLTree.find("size")
        Size = [int(Size.find("height").text),
                int(Size.find("width").text)]

        h_ratio = 1.0 * self.ImageSize / Size[0]
        w_ratio = 1.0 * self.ImageSize / Size[1]

        ObjectCount = 0
        for Object in Objects:
            Box = Object.find("bndbox")
            x1 = max(min((float(Box.find('xmin').text) - 1) * w_ratio, self.ImageSize - 1), 0)
            x2 = max(min((float(Box.find('xmax').text) - 1) * w_ratio, self.ImageSize - 1), 0)
            y1 = max(min((float(Box.find('ymin').text) - 1) * h_ratio, self.ImageSize - 1), 0)
            y2 = max(min((float(Box.find('ymax').text) - 1) * h_ratio, self.ImageSize - 1), 0)

            class_id = self.ClassesDict[Object.find("name").text.lower().strip()]
            BoxInfo = [(x1 + x2) / 2.0, (y1 + y2) / 2.0, x2 - x1, y2 - y1]

            Cell_x = int(BoxInfo[0] * self.CellNum / self.ImageSize)
            Cell_y = int(BoxInfo[1] * self.CellNum / self.ImageSize)

            if label[Cell_x, Cell_y, 0] == 1:  # this cell already has an object
                continue
            else:
                ObjectCount += 1
                # format: hasObject[0] boxinfo[1:5] class_id[5]
                label[Cell_x, Cell_y, 0] = 1
                label[Cell_x, Cell_y, 1:5] = BoxInfo
                label[Cell_x, Cell_y, 5] = class_id

        return label, ObjectCount


if __name__ == "__main__":
    data = PascalVOC()

    # get image sample
    index = int(input("Index of image to show: "))

    while True:
        sample = data.TrainData[index]
        image_path = sample["ImagePath"]
        label = sample["Label"]

        image = cv.imread(image_path)
        image = cv.resize(image, (448, 448))
        cv.putText(image,
                   str(index)+image_path,
                   (0,12),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
        cv.imshow("InitImage", image)
        for i in label:
            for ii in i:
                if ii[0] != 0.0:
                    cv.rectangle(image,
                                 (int(ii[1] - ii[3] / 2), int(ii[2] - ii[4] / 2)),
                                 (int(ii[1] + ii[3] / 2), int(ii[2] + ii[4] / 2)),
                                 (0, 255, 0),
                                 2)
                    cv.putText(image,
                               cfg.Classes[int(ii[5])],
                               (int(ii[1] - ii[3] / 2+2), int(ii[2] - ii[4] / 2)+12),
                               cv.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0))
        cv.imshow("LabeledImage", image)
        cv.waitKey()
        index += 1
