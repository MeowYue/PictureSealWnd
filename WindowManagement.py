import sys
import os
import random
from PySide2 import QtCore, QtWidgets, QtGui
import MainProgram

class PicSealMainWnD(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Flipbook 拼图")
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.sealing = False
        self.rows = 0

    def create_widgets(self):
        self.folderSelectionButton = QtWidgets.QPushButton("选择目录")
        self.text = QtWidgets.QLabel("文件目录:")
        self.pathEditLine = QtWidgets.QLineEdit()
        self.RowsSelectButton = QtWidgets.QPushButton("选择行数")
        self.RowsSelectButton.setDisabled(True)
        #self.quitButton = QtWidgets.QPushButton("退出")
        self.infoLabel = QtWidgets.QLabel("请在上方选择图片所在文件夹，然后指定行数，开始前请保证文件名顺序正确且不含非图片文件")
        self.startSealButton = QtWidgets.QPushButton("开始拼接")
    
    def create_layouts(self):
        #文件夹选择行
        folderSelectionLayout = QtWidgets.QHBoxLayout()
        folderSelectionLayout.addWidget(self.text)
        folderSelectionLayout.addWidget(self.pathEditLine)
        folderSelectionLayout.addWidget(self.folderSelectionButton)
        #行选择行
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.RowsSelectButton)
        #button_layout.addWidget(self.quitButton)
        #信息行，文件加载完成且选择行数后变为开始拼接行
        info_layout = QtWidgets.QHBoxLayout()
        info_layout.addWidget(self.infoLabel)
        info_layout.addStretch()
        info_layout.addWidget(self.startSealButton)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(folderSelectionLayout)
        self.main_layout.addLayout(button_layout)
        self.main_layout.addLayout(info_layout)
        self.startSealButton.setVisible(False)

    def create_connections(self):
        self.folderSelectionButton.clicked.connect(self.getFileFolder)
        self.RowsSelectButton.clicked.connect(self.startSeal)
        self.pathEditLine.textChanged.connect(self.check_path_avaliable)
        

    def check_path_avaliable(self,currPath):
        if(os.path.exists(currPath)):
            self.RowsSelectButton.setDisabled(False)
        else:
            self.RowsSelectButton.setDisabled(True)

    def getFileFolder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选取全是图片的文件夹", "./")
        self.pathEditLine.setText(directory)
        if(directory != ""):
            self.RowsSelectButton.setDisabled(False)

    def startSeal(self):
        self.file_paths = MainProgram.LoadFiles(self.pathEditLine.text())
        factors = MainProgram.allFactor(len(self.file_paths))
        self.rowDialog = RowSelectWindow(factors)
        self.rowDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.rowDialog.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.rowDialog.confirmButton.clicked.connect(self.getRows)
        self.rowDialog.show()

    #获得行数并计算最终矩阵，此函数在子窗口中被调用
    def getRows(self):
        self.rowDialog.loadingLabel.setText("正在加载文件...")
        index = self.rowDialog.rowsCombobox.currentIndex()
        self.selectedRows = int(self.rowDialog.rows[index])
        #创建了缝图实例
        self.picSealInstance =MainProgram.PicSealInstance(MainProgram.createArray(self.file_paths,self.selectedRows),self.file_paths)
        self.rowDialog.close()
        self.infoLabel.setText("所选目录图片总数为{0}，即将输出排列为{1}的Flipbook，点击右边按钮开始拼接".format(str(self.picSealInstance.tileSize[1]*self.picSealInstance.tileSize[0]),str(self.picSealInstance.tileSize)))
        #灰化所有之前的按钮和路径，绑定缝图实例的函数到开始拼接上
        self.pathEditLine.setDisabled(True)
        self.folderSelectionButton.setDisabled(True)
        self.RowsSelectButton.setDisabled(True)
        self.startSealButton.clicked.connect(self.startSealThreads)
        self.startSealButton.setVisible(True)

    def startSealThreads(self):
        self.picSealInstance.startExecuteThreads()
        fileExisted = os.path.isfile(os.getcwd() +"\\"+"flipbook.png")
        self.completionDialog = OutputInfomationWindow(fileExisted)
        self.completionDialog.show()
        self.completionDialog.confirm.clicked.connect(self.saveImageFile)
        #TODO 将该对话框的确定按键绑定为保存图片的函数，该函数在缝图实例中进行实现，在主窗口中引用，在主窗口类中绑定

    def saveImageFile(self):
        fileName = "flipbook" if not self.completionDialog.existed else self.completionDialog.fileName.text()
        finalFilePath = os.getcwd() +"\\" + fileName + ".png"
        self.picSealInstance.saveCurrentFile(finalFilePath)
        self.allFinishedInfomation()
        self.completionDialog.close()
        

    def allFinishedInfomation(self):
        self.finalWnD = QuitDialog()
        self.finalWnD.show()
        self.finalWnD.infoLabel.setText("拼接完毕！\n 最终排列为{0}x{1}的Flipbook，请按需填写到VFX软件".format(str(self.picSealInstance.tileSize[0]),str(self.picSealInstance.tileSize[1])))
        self.finalWnD.confirm.clicked.connect(self.quit_all)

    def quit_all(self):
        os.system('explorer.exe %s' % os.getcwd())
        self.finalWnD.close()
        self.close()

class RowSelectWindow(QtWidgets.QDialog):
    def __init__(self,rows,parent = PicSealMainWnD):
        super(RowSelectWindow,self).__init__()
        self.rows = [str(row) for row in rows]
        self.setWindowTitle("选择行数")
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.rowsCombobox = QtWidgets.QComboBox()
        self.rowsCombobox.addItems(self.rows)
        self.loadingLabel = QtWidgets.QLabel("")
        self.confirmButton = QtWidgets.QPushButton("确认")
        
    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("选择Flipbook行数",self.rowsCombobox)
        form_layout.addRow(self.loadingLabel)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirmButton)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        pass

class OutputInfomationWindow(QtWidgets.QDialog):
    def __init__(self,existed,parent=PicSealMainWnD):
        super(OutputInfomationWindow,self).__init__()
        self.setWindowTitle("拼接完毕")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.existed = existed
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.infomation = QtWidgets.QLabel()
        self.fileName = QtWidgets.QLineEdit()
        self.confirm = QtWidgets.QPushButton("确定")

    def create_layouts(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm)
        if(self.existed):
            main_layout = QtWidgets.QVBoxLayout(self)
            self.infomation.setText("当前目录已经存在 flipbook.png ，请设置一个新的名字(不含扩展名)：")
            main_layout.addWidget(self.infomation)
            main_layout.addWidget(self.fileName)
            main_layout.addLayout(button_layout)
        else:
            main_layout = QtWidgets.QVBoxLayout(self)
            self.infomation.setText("拼接后的图片将被保存到*本程序目录*下的flipbook.png中")
            main_layout.addWidget(self.infomation)
            main_layout.addLayout(button_layout)

    def create_connections(self):
        pass

class QuitDialog(QtWidgets.QDialog):
    def __init__(self,parent=PicSealMainWnD):
        super(QuitDialog,self).__init__()
        self.setWindowTitle("拼接完毕")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.infoLabel = QtWidgets.QLabel()
        self.confirm = QtWidgets.QPushButton("关闭并打开所在文件夹")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.infoLabel)
        main_layout.addWidget(self.confirm)

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    widget = PicSealMainWnD()
    widget.resize(800, 100)
    widget.show()

    sys.exit(app.exec_())