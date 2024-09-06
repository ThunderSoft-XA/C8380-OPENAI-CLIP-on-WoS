# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_images_by_text.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 650)
        font = QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.mainQFrame = QFrame(self.centralwidget)
        self.mainQFrame.setObjectName(u"mainQFrame")
        self.mainQFrame.setStyleSheet(u"")
        self.mainQFrame.setFrameShape(QFrame.StyledPanel)
        self.mainQFrame.setFrameShadow(QFrame.Raised)
        self.label1 = QLabel(self.mainQFrame)
        self.label1.setObjectName(u"label1")
        self.label1.setGeometry(QRect(0, 10, 75, 21))
        font1 = QFont()
        font1.setPointSize(11)
        self.label1.setFont(font1)
        self.label2 = QLabel(self.mainQFrame)
        self.label2.setObjectName(u"label2")
        self.label2.setGeometry(QRect(0, 40, 75, 21))
        self.label2.setFont(font1)
        self.directoryLineEdit = QLineEdit(self.mainQFrame)
        self.directoryLineEdit.setObjectName(u"directoryLineEdit")
        self.directoryLineEdit.setEnabled(False)
        self.directoryLineEdit.setGeometry(QRect(80, 5, 1020, 30))
        self.directoryLineEdit.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border: 1px solid rgb(0, 0, 0);")
        self.textDescriptionTextEdit = QTextEdit(self.mainQFrame)
        self.textDescriptionTextEdit.setObjectName(u"textDescriptionTextEdit")
        self.textDescriptionTextEdit.setGeometry(QRect(80, 40, 1020, 100))
        self.textDescriptionTextEdit.setStyleSheet(u"background-color: rgba(255, 255, 255, 240);\n"
"border: 1px solid rgb(0, 0, 0);")
        self.selectDirectoryButton = QPushButton(self.mainQFrame)
        self.selectDirectoryButton.setObjectName(u"selectDirectoryButton")
        self.selectDirectoryButton.setGeometry(QRect(1110, 0, 70, 30))
        self.selectDirectoryButton.setFont(font1)
        self.selectDirectoryButton.setLayoutDirection(Qt.RightToLeft)
        self.searchImagesButton = QPushButton(self.mainQFrame)
        self.searchImagesButton.setObjectName(u"searchImagesButton")
        self.searchImagesButton.setGeometry(QRect(1110, 40, 70, 30))
        self.searchImagesButton.setFont(font1)
        self.label2_2 = QLabel(self.mainQFrame)
        self.label2_2.setObjectName(u"label2_2")
        self.label2_2.setGeometry(QRect(0, 150, 75, 21))
        self.label2_2.setFont(font1)
        self.imageListWidget = QListWidget(self.mainQFrame)
        self.imageListWidget.setObjectName(u"imageListWidget")
        self.imageListWidget.setGeometry(QRect(0, 180, 1181, 420))
        self.imageListWidget.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"")
        self.imageListWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imageListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.horizontalLayout.addWidget(self.mainQFrame)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 19))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setFont(font1)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u56fe\u50cf\u641c\u7d22(openai CLIP)", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u8def\u5f84:", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"\u6587\u672c\u63cf\u8ff0:", None))
        self.selectDirectoryButton.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9", None))
        self.searchImagesButton.setText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
        self.label2_2.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u7247\u6982\u89c8\uff1a", None))
    # retranslateUi

