#-*-coding: UTF-8-*-
######################################################################
##   OpenSeesPyGUI- A pre and post process GUI for the OpenSeesPy   ##
##   (C) Copyright 2022 Department of bridge engineering,Tongji     ##
##   University, All rights reserved.                               ##
##                                                                  ##
##   Developed by:                                                  ##
##     Junjun Guo (guojj@tongji.edu.cn)                             ##
######################################################################
#  Environemet: Successfully excucted in python 3.8
#########################################################################
#import necessary modules
import sys
import os
import ctypes
import functools
import time
import ezdxf
user32=ctypes.windll.user32
os.environ["QT_API"] = "pyqt5"
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication,QColorDialog,QMenu,QToolBar,QAction,QFileDialog,QVBoxLayout,QHBoxLayout,
                             QLabel,QLineEdit,QPushButton,QFrame,QStatusBar,QComboBox,QSplitter,QGroupBox,
                             QSpacerItem,QSizePolicy)
from PyQt5.QtGui import (QIcon,QPalette,QColor,QFont)
from PyQt5.QtCore import (QDir,Qt)
import numpy as np
import pyvista as pv
from pyvistaqt import (QtInteractor)
import records
from defaultSettingDB import DefaultSet
from SqliteDB import SqliteDB  ##sqlite database to store opensees results
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvas,NavigationToolbar2QT as NavigationToolbar)
########################################################################################################################
########################################################################################################################
class MainWindow(QtWidgets.QMainWindow):
    """---main window establishment based on pyqt5 and pyvista---"""
    def __init__(self):
        super(MainWindow,self).__init__()
        self.resourcePath=os.getcwd()
        print(self.resourcePath)
        self.screenSize=user32.GetSystemMetrics(0),user32.GetSystemMetrics(1)
        self.cadVersionDict={"AutoCAD_R2000":"AC1015","AutoCAD_R2004":"AC1018","AutoCAD_R2007":"AC1021",
                             "AutoCAD_R2010":"AC1024","AutoCAD_R2013":"AC1027","AutoCAD_R2018":"AC1032"}
        self.nodeNameList = []
        self.eleNameList = []
        self.modalNameList = []
        self.geomTransfNameList=[]
        self.eleLocalCoordSysNameList=[]
        self.toolBar()
        self.ui()
        self.statusBarSetting()
        self.menu()

    def ui(self):
        """---basic panel setting---"""
        self.setWindowTitle("OpenSeesPyGUI")
        self.setWindowIcon(QIcon(self.resourcePath+"/OpenSeesPyGUI.ico"))
        self.setGeometry(int(0.05 * self.screenSize[0]), int(0.1 * self.screenSize[1]), \
                         int(0.9 * self.screenSize[0]), int(0.8 * self.screenSize[1]))
        self.frame = QFrame()  # generate frame
        vlayout = QVBoxLayout()
        self.plotter = QtInteractor(self.frame)  # add pyvista interactor
        vlayout.addWidget(self.plotter.interactor)
        self.frame.setLayout(vlayout)
        self.setCentralWidget(self.frame)
        self.plotter.view_vector((-0.5, -1, 1), viewup=None)
        self.plotter.add_axes(x_color="red", y_color="green", z_color="blue")
        self.plotter.enable_parallel_projection()

    def statusBarSetting(self):
        """---statusbar setting---"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.author = QLabel("Author:Junjun Guo")
        self.email = QLabel("Email:guojj@tongji.edu.cn")
        self.home = QLabel("Copyright © 2022 Department of bridge engineering,Tongji University, All rights reserved.")
        self.version = QLabel("Version=0.1.0")
        self.statusBar.addPermanentWidget(self.author, stretch=1)
        self.statusBar.addPermanentWidget(self.email, stretch=2)
        self.statusBar.addPermanentWidget(self.home, stretch=3)
        self.statusBar.addPermanentWidget(self.version, stretch=1)

    def menu(self):
        """---menu bar setting---"""
        mainMenu = self.menuBar()  # menu bar
        self.optionMenu(mainMenu)  # select menu setting
        self.postProcess(mainMenu) # post process menu setting

    def optionMenu(self, mainMenu):
        """---select menu setting---"""
        optionMenu = mainMenu.addMenu("&Option")
        #########################################################
        backGroundColorAction = QAction('backGroundColor', self)
        # signal and slot for background color setting
        backGroundColorAction.triggered.connect(self.backGroundColorChangeSlot)
        #########################################################
        self.colorMenu = QMenu("&Color...", self)
        self.colorMenu.addAction(backGroundColorAction)
        optionMenu.addMenu(self.colorMenu)
        #########################################################
        nodeColorAction = QAction('nodeColor', self)
        self.colorMenu.addAction(nodeColorAction)
        # signal and slot for node color setting
        nodeColorAction.triggered.connect(self.nodeColorChangeSlot)
        #########################################################
        nodeTagColorAction = QAction('nodeTagColor', self)
        self.colorMenu.addAction(nodeTagColorAction)
        # signal and slot for node tag color setting
        nodeTagColorAction.triggered.connect(self.nodeTagColorChangeSlot)
        #########################################################
        eleTagAction = QAction('eleTagColor', self)
        self.colorMenu.addAction(eleTagAction)
        eleTagAction.triggered.connect(self.eleTagColorChangeSlot)
        #########################################################
        modeInitAction = QAction('modeInitColor', self)
        self.colorMenu.addAction(modeInitAction)
        modeInitAction.triggered.connect(self.modeInitColorChangeSlot)
        #########################################################
        modeUpdateAction = QAction('modeUpdateColor', self)
        self.colorMenu.addAction(modeUpdateAction)
        modeUpdateAction.triggered.connect(self.modeUpdateColorChangeSlot)
        #########################################################

    def postProcess(self,mainMenu):
        """---post process menu setting---"""
        postProcessMenu = mainMenu.addMenu('&PostProcess')
        timeHistoryPlotAction = QAction('&responsesPlot', self)
        postProcessMenu.addAction(timeHistoryPlotAction)
        timeHistoryPlotAction.triggered.connect(self.timeHistoryPlotSlot)
        
    def backGroundColorChangeSlot(self):
        """---slot function for background color change setting---"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.plotter.set_background(color.name())
            DefaultSet.upDateValue(tableName="backGroundColorTable",
                                   tagName="backGroundColor", tagValue=color.name())

    def nodeColorChangeSlot(self):
        """---slot function for node color setting---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName="nodeColorTable",
                                   tagName="nodeColor", tagValue=color.name())
            self.nodeBarSlot()

    def nodeTagColorChangeSlot(self):
        """---slot function for node tag color setting---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName="nodeTagColorTable",
                                   tagName="nodeTagColor", tagValue=color.name())
            self.nodeTagBarSlot()

    def eleTagColorChangeSlot(self):
        """---slot function for elment tag color change---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName="eleTagColorTable",
                                   tagName="eleTagColor", tagValue=color.name())
            self.eleNodeTagBarSlot()

    def modeInitColorChangeSlot(self):
        """---slot function for mode init color change---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName="modeInitColorTable",
                                   tagName="modeInitColor", tagValue=color.name())

    def timeHistoryPlotSlot(self):
        """---slot function for time history response plot---"""
        self.timeHistoryPlotClassInstance = TimeHistoryPlotClass(self.dbPath)
        self.timeHistoryPlotClassInstance.show()

    def modeUpdateColorChangeSlot(self):
        """---slot function for mode update color change---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName="modeUpdateColorTable",
                                   tagName="modeUpdateColor", tagValue=color.name())

    def toolBar(self):
        """---tool bar setting---"""
        self.mainToolBar = QToolBar()
        self.mainToolBar.setAutoFillBackground(True)
        self.mainToolBar.setPalette(QPalette(QColor("white")))
        self.addToolBar(Qt.TopToolBarArea, self.mainToolBar)
        ##################################################################
        self.loadDbBar(self.mainToolBar)
        self.nodeBar(self.mainToolBar)
        self.nodeTagBar(self.mainToolBar)
        self.eleBar(self.mainToolBar)
        self.eleNodeBar(self.mainToolBar)
        self.eleNodeTagBar(self.mainToolBar)
        self.localZBar(self.mainToolBar)
        self.mainToolBar.addSeparator()
        self.initBar(self.mainToolBar)
        self.mainToolBar.addSeparator()
        self.threeDimBar(self.mainToolBar)
        self.xyViewBar(self.mainToolBar)
        self.xzViewBar(self.mainToolBar)
        self.yzViewBar(self.mainToolBar)
        self.mainToolBar.addSeparator()
        self.modalNameLabelBar(self.mainToolBar)
        self.modalLineEditBar(self.mainToolBar)
        self.scaleLabelBar(self.mainToolBar)
        self.scaleLineEditBar(self.mainToolBar)
        self.periodNameLabelBar(self.mainToolBar)
        self.periodLineEditBar(self.mainToolBar)
        self.staticModeButtonBar(self.mainToolBar)
        self.dynamicModeButtonBar(self.mainToolBar)
        self.cadVersionComBoBar(self.mainToolBar)
        self.exportModelButtonBar(self.mainToolBar)
        self.exportModeShapeButtonBar(self.mainToolBar)
        self.mainToolBar.addSeparator()

    def loadDbBar(self,mainToolBar):
        """load result database"""
        btn_loadResult = QPushButton("loadResultDB")
        btn_loadResult.setFont(QFont('Times', 10))
        mainToolBar.addWidget(btn_loadResult)
        btn_loadResult.clicked.connect(self.loadDbBarSlot)

    def loadDbBarSlot(self):
        """load result database"""
        curDir = QDir.currentPath()
        try:
            aFile, filt = QFileDialog.getOpenFileName(self, "Open result database", curDir, "(*.db)")  # file dialog
            self.dbPath =aFile
            self._dataBaseProcess(self.dbPath)
            self._eleColorAction()
        except:
            print("The result database is wrong!")

    def _eleColorAction(self):
        """set element color action"""
        for eachName in self.eleNameList:
            eachAction = QAction(eachName, self)
            self.colorMenu.addAction(eachAction)
            eachAction.triggered.connect(functools.partial(self.elesColorChangeSlot, eachName))

    def elesColorChangeSlot(self, elesName):
        """---elements color setting---"""
        color = QColorDialog.getColor()
        if color.isValid():
            DefaultSet.upDateValue(tableName=elesName + "Table",
                                   tagName=elesName + "Color", tagValue=color.name())
            self.elesBarSlot()

    def _dataBaseProcess(self,dbPath):
        """process the result database"""
        self.sqliteDBInstance = SqliteDB(dbPath)
        db = records.Database('sqlite:///' + dbPath)
        tableNames = db.get_table_names()
        modalNameList=[]
        for each in tableNames:
            if each=='periods':
                continue
            else:
                splitList=each.rsplit('_')
                if splitList[1]=='node':
                    self.nodeNameList.append(each)
                elif splitList[1]=='ele':
                    self.eleNameList.append(each)
                elif splitList[1]=='mode':
                    modalNameList.append(splitList)
                elif splitList[1]=='geomTransf':
                    self.geomTransfNameList.append(each)
                elif splitList[1]=='eleLocCordSys':
                    self.eleLocalCoordSysNameList.append(each)
        modalName=modalNameList[0][0]+'_'+modalNameList[0][1]
        self.modalNameList.append(modalName)

    def nodeBar(self, mainToolBar):
        """---model nodes tool set---"""
        nodeAct = QAction(QIcon(self.resourcePath+"/node.png"), "node", self)
        mainToolBar.addAction(nodeAct)
        nodeAct.triggered.connect(self.nodeBarSlot)

    def nodeBarSlot(self):
        """---model nodes plot slot---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.nodesPlot(self.nodeNameList, self.sqliteDBInstance)

    def nodeTagBar(self, mainToolBar):
        """---model nodes and tags set---"""
        nodeTagAct = QAction(QIcon(self.resourcePath+"/nodeTag.png"), "nodeTag", self)
        mainToolBar.addAction(nodeTagAct)
        nodeTagAct.triggered.connect(self.nodeTagBarSlot)

    def nodeTagBarSlot(self):
        """---model nodes and tags plot slot---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.nodesTagPlot(self.nodeNameList, self.sqliteDBInstance)

    def eleBar(self, mainToolBar):
        """---model elements set---"""
        elesAct = QAction(QIcon(self.resourcePath+"/element.png"), "elements", self)
        mainToolBar.addAction(elesAct)
        elesAct.triggered.connect(self.elesBarSlot)

    def elesBarSlot(self):
        """---model elements plot slot---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.elesPlot(self.nodeNameList, self.sqliteDBInstance, self.eleNameList)

    def eleNodeBar(self, mainToolBar):
        """---model elements and nodes set---"""
        eleNodeAct = QAction(QIcon(self.resourcePath+"/eleNodes.png"), "elements and nodes", self)
        mainToolBar.addAction(eleNodeAct)
        eleNodeAct.triggered.connect(self.eleNodeBarSlot)

    def eleNodeBarSlot(self):
        """---model elements and nodes plot slot---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.eleNodePlot(self.nodeNameList, self.sqliteDBInstance, self.eleNameList)

    def eleNodeTagBar(self, mainToolBar):
        """---model elments ,nodes and tags set---"""
        eleNodeTagAct = QAction(QIcon(self.resourcePath+"/nodeEleTag.png"), "elements,nodes and tags", self)
        mainToolBar.addAction(eleNodeTagAct)
        eleNodeTagAct.triggered.connect(self.eleNodeTagBarSlot)

    def eleNodeTagBarSlot(self):
        """---model elements, nodes and tags plot slot---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.eleNodeTagPlot(self.nodeNameList, self.sqliteDBInstance, self.eleNameList)

    def localZBar(self,mainToolBar):
        """---local coordinate system of each element set---"""
        localZAct = QAction(QIcon(self.resourcePath + "/eleLocalZTag.png"), "element local coordinate system", self)
        mainToolBar.addAction(localZAct)
        localZAct.triggered.connect(self.localZBarSlot)

    def localZBarSlot(self):
        """---element local coordinate system plot slot ---"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.localZPlot(self.nodeNameList,self.sqliteDBInstance, self.eleNameList,self.geomTransfNameList,
                                self.eleLocalCoordSysNameList)

    def initBar(self, mainToolBar):
        """---reset view to default---"""
        initAct = QAction(QIcon(self.resourcePath+"/init.png"), "default view", self)
        mainToolBar.addAction(initAct)
        initAct.triggered.connect(self.initBarSlot)

    def initBarSlot(self):
        """---reset view to default view slot---"""
        self.plotter.view_vector((-0.5, -1, 1), viewup=None)

    def threeDimBar(self, mainToolBar):
        """---3D view set---"""
        threeDimAct = QAction(QIcon(self.resourcePath+"/threeDim.png"), "three dimensional view", self)
        mainToolBar.addAction(threeDimAct)
        threeDimAct.triggered.connect(self.threeDimBarSlot)

    def threeDimBarSlot(self):
        """---3D view tool slot---"""
        self.plotter.isometric_view_interactive()

    def xyViewBar(self, mainToolBar):
        """---xy view set---"""
        xyViewAct = QAction(QIcon(self.resourcePath+"/XYView.png"), "XY view", self)
        mainToolBar.addAction(xyViewAct)
        xyViewAct.triggered.connect(self.xyViewBarSlot)

    def xyViewBarSlot(self):
        """---xy view tool slot---"""
        self.plotter.view_xy(negative=False)

    def xzViewBar(self, mainToolBar):
        """---xz view set---"""
        xzViewAct = QAction(QIcon(self.resourcePath+"/XZView.png"), "XZ view", self)
        mainToolBar.addAction(xzViewAct)
        xzViewAct.triggered.connect(self.xzViewBarSlot)

    def xzViewBarSlot(self):
        """---xz view tool slot---"""
        self.plotter.view_xz(negative=False)

    def yzViewBar(self, mainToolBar):
        """---yz view set---"""
        yzViewAct = QAction(QIcon(self.resourcePath+"/YZView.png"), "YZ view", self)
        mainToolBar.addAction(yzViewAct)
        yzViewAct.triggered.connect(self.yzViewBarSlot)

    def yzViewBarSlot(self):
        """---yz view tool slot---"""
        self.plotter.view_yz(negative=True)

    def modalNameLabelBar(self, mainToolBar):
        """add a label"""
        label_modalName = QLabel("Mode:")
        mainToolBar.addWidget(label_modalName)
        label_modalName.setFont(QFont('Times', 10))

    def modalLineEditBar(self, mainToolBar):
        """add a line edit"""
        self.lineEdit_modeNumber = QLineEdit(toolTip="mode number must be integer!")
        self.lineEdit_modeNumber.setMaximumWidth(50)
        self.lineEdit_modeNumber.setAlignment(Qt.AlignHCenter)
        self.lineEdit_modeNumber.setText(str(1))
        mainToolBar.addWidget(self.lineEdit_modeNumber)

    def scaleLabelBar(self, mainToolBar):
        """addd a label"""
        label_scale = QLabel("Scale:")
        mainToolBar.addWidget(label_scale)
        label_scale.setFont(QFont('Times', 10))

    def scaleLineEditBar(self, mainToolBar):
        """add a line edit"""
        self.lineEdit_scale = QLineEdit()
        self.lineEdit_scale.setMaximumWidth(50)
        self.lineEdit_scale.setAlignment(Qt.AlignHCenter)
        self.lineEdit_scale.setText(str(1))
        mainToolBar.addWidget(self.lineEdit_scale)

    def periodNameLabelBar(self, mainToolBar):
        """add  a label"""
        label_periodName = QLabel("Period:")
        mainToolBar.addWidget(label_periodName)
        label_periodName.setFont(QFont('Times', 10))

    def periodLineEditBar(self, mainToolBar):
        """add a line edit"""
        self.lineEdit_period = QLineEdit(toolTip="unit in second!")
        self.lineEdit_period.setMaximumWidth(80)
        self.lineEdit_period.setAlignment(Qt.AlignHCenter)
        mainToolBar.addWidget(self.lineEdit_period)

    def staticModeButtonBar(self, mainToolBar):
        """add a button"""
        btn_plotMode = QPushButton("staticMode")
        btn_plotMode.setFont(QFont('Times', 10))
        mainToolBar.addWidget(btn_plotMode)
        btn_plotMode.clicked.connect(self.staticModeButtonBarSlot)

    def staticModeButtonBarSlot(self):
        """modal button click slot"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.staticModePlot(self.nodeNameList, self.sqliteDBInstance, self.eleNameList, self.modalNameList,
                                    self.lineEdit_modeNumber, self.lineEdit_period, self.lineEdit_scale)

    def dynamicModeButtonBar(self, mainToolBar):
        """add a button"""
        btn_plotMode = QPushButton("dynamicMode")
        btn_plotMode.setFont(QFont('Times', 10))
        mainToolBar.addWidget(btn_plotMode)
        btn_plotMode.clicked.connect(self.dynamicModeButtonBarSlot)

    def dynamicModeButtonBarSlot(self):
        """dynamic mode button click slot"""
        plotInstance = pyvistaPlotClass(self.plotter)
        plotInstance.dynamicModePlot(self.nodeNameList, self.sqliteDBInstance, self.eleNameList, self.modalNameList,
                                     self.lineEdit_modeNumber, self.lineEdit_period, self.lineEdit_scale)

    def cadVersionComBoBar(self,mainToolBar):
        """add a combo box"""
        self.qcbox_cadVersion = QComboBox()
        self.qcbox_cadVersion.setFixedHeight(26)
        self.qcbox_cadVersion.addItems(["AutoCAD_R2000", "AutoCAD_R2004", "AutoCAD_R2007","AutoCAD_R2010",
                                   "AutoCAD_R2013","AutoCAD_R2018"])
        mainToolBar.addWidget(self.qcbox_cadVersion)

    def exportModelButtonBar(self,mainToolBar):
        """add a button"""
        btn_exportModel = QPushButton("exportModel")
        btn_exportModel.setFont(QFont('Times', 10))
        mainToolBar.addWidget(btn_exportModel)
        btn_exportModel.clicked.connect(self.exportModelSlot)

    def exportModelSlot(self):
        """
        export model to cad dxf click slot
        point Mode:
        0-center dot(.), 1 none,2 cross(+),3 cross(x),4 tick('),32 circle,64 square, others are combed
        e.g. circle+square+center dot=32+64+0=96
        point size:
        0-5% of draw area height
        <0-specifies a percentage of the viewport size
        >0-specifies an absolute siz
        """
        saveFolder=QFileDialog.getExistingDirectory(self, "Please select a save folder", "")
        cadRelease=self.qcbox_cadVersion.currentText()
        cadVersion=self.cadVersionDict[cadRelease]
        doc = ezdxf.new(cadVersion)# Add new entities to the modelspace
        doc.header["$PDMODE"] =0
        doc.header["$PDSIZE"] =0
        msp = doc.modelspace()
        nodesReturnList = []
        for nodeName in self.nodeNameList:
            getNodes = self.sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesCoordList = [eval(each['contents']) for each in nodesReturnList]
        [msp.add_point((each[0],each[1],each[2]),dxfattribs={"color": 1},) for each in nodesCoordList]
        nodesDict={each["tags"]:eval(each["contents"]) for each in nodesReturnList}
        colorList=[2,3,4,5,6,7,8,9]
        colorIndex=0
        for eachEleName in self.eleNameList:
            getEles = self.sqliteDBInstance.getEles(eachEleName)
            eleNodes=[eval(each['contents']) for each in getEles]
            colorIndex = colorIndex + 1
            [msp.add_line(nodesDict[nodeIJ[0]],nodesDict[nodeIJ[1]],dxfattribs={"color":colorList[colorIndex]},)
             for nodeIJ in eleNodes]
            colorIndex=colorIndex%len(colorList)
        doc.saveas(saveFolder+"/modelPlot.dxf")

    def exportModeShapeButtonBar(self,mainToolBar):
        """Add a button"""
        btn_exportModeShape = QPushButton("exportModeShape")
        btn_exportModeShape.setFont(QFont('Times', 10))
        mainToolBar.addWidget(btn_exportModeShape)
        btn_exportModeShape.clicked.connect(self.exportModeShapeSlot)

    def exportModeShapeSlot(self):
        """
        export mode shapes to autocad DXF file
        """
        saveFolder = QFileDialog.getExistingDirectory(self, "Please select a save folder", "")
        scaleValue = float(self.lineEdit_scale.text())
        modelNum = int(self.lineEdit_modeNumber.text())
        cadRelease = self.qcbox_cadVersion.currentText()
        cadVersion = self.cadVersionDict[cadRelease]
        doc = ezdxf.new(cadVersion)
        msp = doc.modelspace()
        getModes = self.sqliteDBInstance.getModes(self.modalNameList[0] + '_' + str(modelNum))
        modesDict = {each['tags']: eval(each['contents']) for each in getModes}
        nodesReturnList = []
        for nodeName in self.nodeNameList:
            getNodes = self.sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = {each["tags"]: eval(each["contents"]) for each in nodesReturnList}
        updatedNodesDict = {each["tags"]:[eval(each['contents'])[0] + modesDict[each['tags']][0] * scaleValue,
                                eval(each['contents'])[1] + modesDict[each['tags']][1] * scaleValue,
                                eval(each['contents'])[2] + modesDict[each['tags']][2] * scaleValue, ] for each in
                               nodesReturnList}

        for eachEleName in self.eleNameList:
            getEles = self.sqliteDBInstance.getEles(eachEleName)
            eleNodes = [eval(each['contents']) for each in getEles]
            [msp.add_line(nodesDict[nodeIJ[0]], nodesDict[nodeIJ[1]], dxfattribs={"color": 1,},) for nodeIJ in eleNodes]
            [msp.add_line(updatedNodesDict[nodeIJ[0]], updatedNodesDict[nodeIJ[1]], dxfattribs={"color":3, }, )
             for nodeIJ in eleNodes]
        doc.saveas(saveFolder+"/modeShape_"+str(modelNum)+".dxf")
########################################################################################################################
########################################################################################################################
class pyvistaPlotClass():
    """---figure plot class based on pyvista module---"""
    def __init__(self,plotter):
        self.plotter=plotter
        self.pointSize=4.5
        self.stepNum=20
        self.timeSleepValue=0.002
        self.modeIterNum=3
        self.modeInitLineWidth=0.0001
        self.modeDynamicLineWidth=2

    def nodesPlot(self,nodeNameList,sqliteDBInstance):
        """---model nodes plot---"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesCoordList = [eval(each['contents']) for each in nodesReturnList]
        vertices=np.array(nodesCoordList)
        surf = pv.PolyData(vertices)
        self.plotter.clear()
        nodeColor = DefaultSet.getValue(tableName="nodeColorTable", tagName="nodeColor")
        self.plotter.add_mesh(surf, color=nodeColor, point_size=self.pointSize, render_points_as_spheres=True)
        if self.plotter.camera_position[0]==(-0.5, -1, 1):
            self.plotter.reset_camera()

    def nodesTagPlot(self,nodeNameList,sqliteDBInstance):
        """---model nodes and tags plot---"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesCoordList = [eval(each['contents']) for each in nodesReturnList]
        nodesLabelList= [each['tags'] for each in nodesReturnList]
        vertices = np.array(nodesCoordList)
        surf = pv.PolyData(vertices)
        self.plotter.clear()
        nodeColor = DefaultSet.getValue(tableName="nodeColorTable",
                                        tagName="nodeColor")
        nodeTagColor = DefaultSet.getValue(tableName="nodeTagColorTable",
                                           tagName="nodeTagColor")
        self.plotter.add_mesh(surf, color=nodeColor, point_size=self.pointSize, render_points_as_spheres=True)
        self.plotter.add_point_labels(vertices, nodesLabelList, bold=False, point_size=0.001,
                                      font_size=16, text_color=nodeTagColor, font_family="times", show_points=False,
                                      shape=None,
                                      tolerance=1.0)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()

    @classmethod
    def linkDict(cls, nodesList):
        """---establish sequense dict {23:0,1:1,24:2,...}---"""
        returnDict = {nodesList[each]['tags']: each for each in range(len(nodesList))}
        return returnDict

    def elesPlot(self,nodeNameList,sqliteDBInstance,eleNameList):
        """---model element plot---"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        verticesNodes = [eval(each['contents']) for each in nodesReturnList]
        vertices = np.array(verticesNodes)
        nodeMesh = pv.PolyData(vertices)
        for eachEleName in eleNameList:
            eleColor=DefaultSet.getValue(tableName=eachEleName+"Table",tagName=eachEleName+"Color")
            getEles = sqliteDBInstance.getEles(eachEleName)
            elesNodes=[eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each))  for each in elesNodes]
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(vertices, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True,color=eleColor, style='wireframe', point_size=0)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()


    def eleNodePlot(self,nodeNameList,sqliteDBInstance,eleNameList):
        """---model elements and nodes plot---"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        verticesNodes = [eval(each['contents']) for each in nodesReturnList]
        vertices = np.array(verticesNodes)
        nodeMesh = pv.PolyData(vertices)
        self.plotter.clear()
        nodeColor = DefaultSet.getValue(tableName="nodeColorTable", tagName="nodeColor")
        self.plotter.add_mesh(nodeMesh, color=nodeColor, point_size=self.pointSize, render_points_as_spheres=True)
        for eachEleName in eleNameList:
            eleColor=DefaultSet.getValue(tableName=eachEleName+"Table",tagName=eachEleName+"Color")
            getEles = sqliteDBInstance.getEles(eachEleName)
            elesNodes=[eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each))  for each in elesNodes]
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(vertices, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True,color=eleColor, style='wireframe', point_size=0)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()

    def eleTagLocList(self, eleList, nodesTagDict):
        """---calculate element tag position list---"""
        eleLocList = []
        eleNumList = []
        for each in eleList:
            xCoord = []
            yCoord = []
            zCoord = []
            nodesTag = list(map(lambda item: nodesTagDict[item], each[1:]))
            meanValue = [[xCoord.append(each1[0] / len(nodesTag)), yCoord.append(each1[1] / len(nodesTag)),
                          zCoord.append(each1[2] / len(nodesTag))] for each1 in nodesTag]
            eleLocList.append([sum(xCoord), sum(yCoord), sum(zCoord)])
            eleNumList.append(each[0])
        return eleLocList, eleNumList

    def eleNodeTagPlot(self,nodeNameList,sqliteDBInstance,eleNameList):
        """---model elements, nodes and tags plot---"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        nodesCoordList = [eval(each['contents']) for each in nodesReturnList]
        nodesLabelList = [each['tags'] for each in nodesReturnList]
        nodesTagDict = {each['tags']: eval(each['contents']) for each in nodesReturnList}
        vertices = np.array(nodesCoordList)
        surf = pv.PolyData(vertices)
        self.plotter.clear()
        nodeColor = DefaultSet.getValue(tableName="nodeColorTable",
                                        tagName="nodeColor")
        nodeTagColor = DefaultSet.getValue(tableName="nodeTagColorTable",
                                           tagName="nodeTagColor")
        self.plotter.add_mesh(surf, color=nodeColor, point_size=self.pointSize, render_points_as_spheres=True)
        self.plotter.add_point_labels(vertices, nodesLabelList, bold=False, point_size=0.001,
                                      font_size=16, text_color=nodeTagColor, font_family="times", show_points=False,
                                      shape=None,tolerance=1.0)
        eleNodeTagColor = DefaultSet.getValue(tableName="eleTagColorTable", tagName="eleTagColor")
        for eachEleName in eleNameList:
            eleColor=DefaultSet.getValue(tableName=eachEleName+"Table",tagName=eachEleName+"Color")
            getEles = sqliteDBInstance.getEles(eachEleName)
            eles=[[each['tags']]+eval(each['contents']) for each in getEles]
            elesNodes = [eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each))  for each in elesNodes]
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(vertices, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True,color=eleColor, style='wireframe', point_size=0)
            eleLocList, eleNumList = self.eleTagLocList(eles, nodesTagDict)
            self.plotter.add_point_labels(np.array(eleLocList), eleNumList, bold=False, point_size=0.001,
                                          font_size=16, text_color=eleNodeTagColor, font_family="times",
                                          show_points=False,shape=None, tolerance=1.0)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()

    def localZPlot(self,nodeNameList,sqliteDBInstance,eleNameList,geomTransfNameList,eleLocalCoordSysNameList):
        """---element local coordinate systems plot----"""
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        nodesCoordList = [eval(each['contents']) for each in nodesReturnList]
        nodesLabelList = [each['tags'] for each in nodesReturnList]
        nodesTagDict = {each['tags']: eval(each['contents']) for each in nodesReturnList}
        vertices = np.array(nodesCoordList)
        surf = pv.PolyData(vertices)
        self.plotter.clear()
        nodeColor = DefaultSet.getValue(tableName="nodeColorTable",
                                        tagName="nodeColor")
        nodeTagColor = DefaultSet.getValue(tableName="nodeTagColorTable",
                                           tagName="nodeTagColor")
        self.plotter.add_mesh(surf, color=nodeColor, point_size=self.pointSize, render_points_as_spheres=True)

        for eachEleName in eleNameList:
            eleColor=DefaultSet.getValue(tableName=eachEleName+"Table",tagName=eachEleName+"Color")
            getEles = sqliteDBInstance.getEles(eachEleName)
            eles=[[each['tags']]+eval(each['contents']) for each in getEles]
            elesNodes = [eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each))  for each in elesNodes]
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(vertices, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True,color=eleColor, style='wireframe', point_size=0)

        geotransfList=[]
        for eachGeomTransfName in geomTransfNameList:
            geomTransfDB = sqliteDBInstance.getGeomTransf(eachGeomTransfName)
            [geotransfList.append([each['tags']]+eval(each['contents'])) for each in geomTransfDB]
        geotransfDict={each[0]:each[1:] for each in geotransfList}
        realLengthEleCoordList=[]
        specialEleCoordList=[]
        for eachEleCoordSysName in eleLocalCoordSysNameList:
            eachEleCoordSysDB = sqliteDBInstance.getEleLocalCoordSys(eachEleCoordSysName)
            [realLengthEleCoordList.append(eval(each['contents'])) if each['tags']=='realEle'
             else specialEleCoordList.append(eval(each['contents'])) for each in eachEleCoordSysDB]
        realLengthEleArrowList=[]
        for each in realLengthEleCoordList:
            nodeI,nodeJ,transfTag=each[0],each[1],each[2]
            nodeICoord=nodesTagDict[nodeI]
            nodeJCoord = nodesTagDict[nodeJ]
            localCoordSysLoc=(0.5*(nodeICoord[0]+nodeJCoord[0]),0.5*(nodeICoord[1]+nodeJCoord[1]),
                              0.5*(nodeICoord[2]+nodeJCoord[2]))
            directionX=(nodeJCoord[0]-nodeICoord[0],nodeJCoord[1]-nodeICoord[1],nodeJCoord[2]-nodeICoord[2])
            directionZ=geotransfDict[transfTag]
            vectorX= np.array(directionX)
            vectorZ=np.array(directionZ)
            vectorY= np.cross(vectorZ,vectorX)
            realLengthEleArrowList.append([localCoordSysLoc,vectorX.tolist(),vectorY.tolist(),vectorZ.tolist()])
        specialEleArrowList=[]
        for each in specialEleCoordList:
            nodeI,nodeJ,localX,localY=each[0],each[1],each[2],each[3]
            localCoordLoc=nodesTagDict[nodeI]
            localZ=np.cross(np.array(localX),np.array(localY))
            specialEleArrowList.append([localCoordLoc,list(localX),list(localY),localZ.tolist()])
        localYList=[]
        localZList=[]
        for each in realLengthEleArrowList:
            localYList.append(list(each[0]))
            localYList.append(list(np.array(each[0])+np.array(each[2])/float(np.linalg.norm(each[2]))))
            localZList.append(list(each[0]))
            localZList.append(list(np.array(each[0])+np.array(each[3])/float(np.linalg.norm(each[3]))))
        vertices = np.array(localYList)
        elesMesh = [[2, int(2 * i1), int(2 * i1 + 1)] for i1 in range(int(0.5 * len(vertices)))]
        elesFaces = np.hstack(elesMesh)
        elesSurf = pv.PolyData(vertices, elesFaces)
        self.plotter.add_mesh(elesSurf, show_edges=True, color='g', style='wireframe', point_size=0,line_width=3,
                              render_lines_as_tubes=True)
        vertices = np.array(localZList)
        elesMesh = [[2, int(2 * i1), int(2 * i1 + 1)] for i1 in range(int(0.5 * len(vertices)))]
        elesFaces = np.hstack(elesMesh)
        elesSurf = pv.PolyData(vertices, elesFaces)
        self.plotter.add_mesh(elesSurf, show_edges=True, color='b', style='wireframe', point_size=0,line_width=3,
                              render_lines_as_tubes=True)
        localXList=[]
        localYList = []
        localZList = []
        for each in specialEleArrowList:
            localXList.append(list(each[0]))
            localXList.append(list(np.array(each[0]) + np.array(each[1]) / float(np.linalg.norm(each[1]))))
            localYList.append(list(each[0]))
            localYList.append(list(np.array(each[0]) + np.array(each[2]) / float(np.linalg.norm(each[2]))))
            localZList.append(list(each[0]))
            localZList.append(list(np.array(each[0]) + np.array(each[3]) / float(np.linalg.norm(each[3]))))

        vertices = np.array(localXList)
        elesMesh = [[2, int(2 * i1), int(2 * i1 + 1)] for i1 in range(int(0.5 * len(vertices)))]
        elesFaces = np.hstack(elesMesh)
        elesSurf = pv.PolyData(vertices, elesFaces)
        self.plotter.add_mesh(elesSurf, show_edges=True, color='r', style='wireframe', point_size=0, line_width=5,
                              render_lines_as_tubes=True)
        vertices = np.array(localYList)
        elesMesh = [[2, int(2 * i1), int(2 * i1 + 1)] for i1 in range(int(0.5 * len(vertices)))]
        elesFaces = np.hstack(elesMesh)
        elesSurf = pv.PolyData(vertices, elesFaces)
        self.plotter.add_mesh(elesSurf, show_edges=True, color='g', style='wireframe', point_size=0, line_width=5,
                              render_lines_as_tubes=True)

        vertices = np.array(localZList)
        elesMesh = [[2, int(2 * i1), int(2 * i1 + 1)] for i1 in range(int(0.5 * len(vertices)))]
        elesFaces = np.hstack(elesMesh)
        elesSurf = pv.PolyData(vertices, elesFaces)
        self.plotter.add_mesh(elesSurf, show_edges=True, color='b', style='wireframe', point_size=0, line_width=5,
                              render_lines_as_tubes=True)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()

    def staticModePlot(self,nodeNameList,sqliteDBInstance,eleNameList,modalNameList,modeLineEdit,periodLineEdit,
                       scaleLineEdit):
        """static mode shape plot"""
        scaleValue=float(scaleLineEdit.text())
        modelNum=int(modeLineEdit.text())
        getPeriods = sqliteDBInstance.getPeriod()
        periodDict={int(each['tags']):eval(each['contents']) for each in getPeriods}
        returnPeriod=periodDict[modelNum][0]
        periodLineEdit.setText(str('%.6f'%(returnPeriod)))
        getModes=sqliteDBInstance.getModes(modalNameList[0]+'_'+str(modelNum))
        modesDict={each['tags']:eval(each['contents']) for each in getModes}
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        verticesNodes = [eval(each['contents']) for each in nodesReturnList]
        vertices = np.array(verticesNodes)
        nodeMesh = pv.PolyData(vertices)
        self.plotter.clear()

        verticesNodesUpdate=[[eval(each['contents'])[0]+modesDict[each['tags']][0]*scaleValue,
                              eval(each['contents'])[1]+modesDict[each['tags']][1]*scaleValue,
                              eval(each['contents'])[2]+modesDict[each['tags']][2]*scaleValue,] for each in nodesReturnList]
        verticesUpdate = np.array(verticesNodesUpdate)
        nodeMeshUpdate = pv.PolyData(verticesUpdate)
        for eachEleName in eleNameList:
            eleColor = DefaultSet.getValue(tableName="modeUpdateColorTable", tagName="modeUpdateColor")
            getEles = sqliteDBInstance.getEles(eachEleName)
            elesNodes = [eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each)) for each in elesNodes]
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(verticesUpdate, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True, color=eleColor, style='wireframe', point_size=0)
        if self.plotter.camera_position[0] == (-0.5, -1, 1):
            self.plotter.reset_camera()

    def dynamicModePlot(self,nodeNameList,sqliteDBInstance,eleNameList,modalNameList,modeLineEdit,periodLineEdit,
                       scaleLineEdit):
        """dynamic mode shape plot"""
        scaleValue = float(scaleLineEdit.text())
        modelNum = int(modeLineEdit.text())
        getPeriods = sqliteDBInstance.getPeriod()
        periodDict = {int(each['tags']): eval(each['contents']) for each in getPeriods}
        returnPeriod = periodDict[modelNum][0]
        periodLineEdit.setText(str('%.6f' % (returnPeriod)))
        getModes = sqliteDBInstance.getModes(modalNameList[0] + '_' + str(modelNum))
        modesDict = {each['tags']: eval(each['contents']) for each in getModes}
        nodesReturnList = []
        for nodeName in nodeNameList:
            getNodes = sqliteDBInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = self.linkDict(nodesReturnList)
        verticesNodes = [eval(each['contents']) for each in nodesReturnList]
        vertices = np.array(verticesNodes)
        nodeMesh = pv.PolyData(vertices)
        self.plotter.clear()
        totalElesMesh=[]
        for eachEleName in eleNameList:
            eleColor = DefaultSet.getValue(tableName="modeInitColorTable", tagName="modeInitColor")
            getEles = sqliteDBInstance.getEles(eachEleName)
            elesNodes = [eval(each['contents']) for each in getEles]
            elesMesh = [[len(each)] + list(map(lambda item: nodesDict[item], each)) for each in elesNodes]
            totalElesMesh+=elesMesh
            elesFaces = np.hstack(elesMesh)
            elesSurf = pv.PolyData(vertices, elesFaces)
            self.plotter.add_mesh(elesSurf, show_edges=True, color=eleColor, style='wireframe', point_size=0,
                                  line_width=self.modeInitLineWidth)
        dynamicEleColor = DefaultSet.getValue(tableName="modeUpdateColorTable", tagName="modeUpdateColor")
        totalElesFace=np.hstack(totalElesMesh)
        totalElesSurf = pv.PolyData(vertices, totalElesFace)
        self.plotter.add_mesh(totalElesSurf, show_edges=True, color=dynamicEleColor, style='wireframe', point_size=0,
                              line_width=self.modeDynamicLineWidth)
        modeCoordsValue = [[modesDict[each['tags']][0] * scaleValue,modesDict[each['tags']][1] * scaleValue,
                        modesDict[each['tags']][2] * scaleValue, ] for each in nodesReturnList]
        for modeIter in range(self.modeIterNum):
            [[self.plotter.update_coordinates(np.array([[vertices[j][0]+modeCoordsValue[j][0]*float(stepCount+1)/float(self.stepNum),
            vertices[j][1]+modeCoordsValue[j][1]*float(stepCount+1)/float(self.stepNum),
            vertices[j][2]+modeCoordsValue[j][2]*float(stepCount+1)/float(self.stepNum)] for j in range(len(vertices))]),
            mesh=totalElesSurf),time.sleep(self.timeSleepValue)] for stepCount in range(self.stepNum)]
            [[self.plotter.update_coordinates(
                np.array([[vertices[j][0] + modeCoordsValue[j][0] * float(self.stepNum-stepCount) / float(self.stepNum),
                           vertices[j][1] + modeCoordsValue[j][1] * float(self.stepNum-stepCount) / float(self.stepNum),
                           vertices[j][2] + modeCoordsValue[j][2] * float(self.stepNum-stepCount) / float(self.stepNum)] for j in
                          range(len(vertices))]),
                mesh=totalElesSurf), time.sleep(self.timeSleepValue)] for stepCount in range(self.stepNum+1)]
            [[self.plotter.update_coordinates(
                np.array([[vertices[j][0] - modeCoordsValue[j][0] * float(stepCount+1) / float(self.stepNum),
                           vertices[j][1] - modeCoordsValue[j][1] * float(stepCount+1) / float(self.stepNum),
                           vertices[j][2] - modeCoordsValue[j][2] * float(stepCount+1) / float(self.stepNum)]
                          for j in range(len(vertices))]),
                mesh=totalElesSurf), time.sleep(self.timeSleepValue)] for stepCount in range(self.stepNum)]
            [[self.plotter.update_coordinates(
                np.array([[vertices[j][0] - modeCoordsValue[j][0] * float(self.stepNum-stepCount) / float(self.stepNum),
                           vertices[j][1] - modeCoordsValue[j][1] * float(self.stepNum-stepCount) / float(self.stepNum),
                           vertices[j][2] - modeCoordsValue[j][2] * float(self.stepNum-stepCount) / float(self.stepNum)]
                          for j in range(len(vertices))]),
                mesh=totalElesSurf), time.sleep(self.timeSleepValue)] for stepCount in range(1,self.stepNum+1)]
        [[self.plotter.update_coordinates(
            np.array([[vertices[j][0] + modeCoordsValue[j][0] * float(stepCount + 1) / float(self.stepNum),
                       vertices[j][1] + modeCoordsValue[j][1] * float(stepCount + 1) / float(self.stepNum),
                       vertices[j][2] + modeCoordsValue[j][2] * float(stepCount + 1) / float(self.stepNum)] for j in
                      range(len(vertices))]),
            mesh=totalElesSurf), time.sleep(self.timeSleepValue)] for stepCount in range(self.stepNum)]

        if self.plotter.camera_position[0]==(-0.5, -1, 1):
            self.plotter.reset_camera()
########################################################################################################################
########################################################################################################################
class TimeHistoryPlotClass(QtWidgets.QMainWindow):
    """---Time history plot class---"""
    def __init__(self,dbPath):
        super(TimeHistoryPlotClass, self).__init__()
        self.dbPath=dbPath
        self.screenSize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.displayFont = QFont()
        self.displayFont.setFamily("Consolas")
        self.displayFont.setPointSize(12)
        self.redColor = "background-color: #ffaa7f"
        self.blueColor = "background-color: #b8f9ff"
        self.statusBarSetting()
        self.ui()

    def statusBarSetting(self):
        """---statusbar setting---"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.author = QLabel("Author:Junjun Guo")
        self.email = QLabel("Email:guojj@tongji.edu.cn")
        self.home = QLabel("Copyright © 2022 Department of bridge engineering,Tongji University, All rights reserved.")
        self.version = QLabel("Version=0.1.0")
        self.statusBar.addPermanentWidget(self.author, stretch=1)
        self.statusBar.addPermanentWidget(self.email, stretch=2)
        self.statusBar.addPermanentWidget(self.home, stretch=3)
        self.statusBar.addPermanentWidget(self.version, stretch=1)

    def ui(self):
        """---time history plot panel setting---"""
        self.setWindowTitle("Post process")
        self.setGeometry(int(0.1 * self.screenSize[0]), int(0.15 * self.screenSize[1]),
                         int(0.8 * self.screenSize[0]), int(0.7 * self.screenSize[1]))
        ######
        self.splitterV1 = QSplitter(orientation=Qt.Vertical)
        frameMatplotlib = QFrame(self.splitterV1)
        self.figure = plt.figure()
        self.figCanvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.figCanvas, self)
        self.ax = self.figure.add_subplot(111)
        ############
        v1Box = QVBoxLayout()
        v1Box.addWidget(self.toolbar)
        v1Box.addWidget(self.figCanvas)
        frameMatplotlib.setLayout(v1Box)

        self.splitterH = QSplitter(orientation=Qt.Horizontal)
        frameLeft = QFrame(self.splitterH)
        v1_1Box = QVBoxLayout()
        v1_1Box.addWidget(self.splitterV1)
        frameLeft.setLayout(v1_1Box)
        ############
        v2_1Box = QVBoxLayout()
        frameResType = QFrame(self.splitterH)
        frameResType.setLayout(v2_1Box)
        nodeGroupBox = QGroupBox("Node-time history")
        v2_1Box.addWidget(nodeGroupBox)
        ###
        trussEleGroupBox=QGroupBox("trussEle-time history")
        v2_1Box.addWidget(trussEleGroupBox)

        zeroEleGroupBox = QGroupBox("zeroEle-time history")
        v2_1Box.addWidget(zeroEleGroupBox)

        nonEleSectGroupBox = QGroupBox("sectEle-time history")
        v2_1Box.addWidget(nonEleSectGroupBox)

        nonZeroEleGroupBox = QGroupBox("nonZeroEle-time history")
        v2_1Box.addWidget(nonZeroEleGroupBox)

        trussEleHysteGroupBox = QGroupBox("trussEle-hysteresis")
        v2_1Box.addWidget(trussEleHysteGroupBox)

        zeroEleHysteGroupBox = QGroupBox("zeroEle-hysteresis")
        v2_1Box.addWidget(zeroEleHysteGroupBox)

        sectEleHysteGroupBox = QGroupBox("sectEle-hysteresis")
        v2_1Box.addWidget(sectEleHysteGroupBox)
        ############
        nodeGroupHBox = QHBoxLayout()
        nodeGroupBox.setLayout(nodeGroupHBox)
        nodeTagLabel= QLabel("nodeTag")
        nodeGroupHBox.addWidget(nodeTagLabel)
        nodeTagLabel.setFont(QFont('Times', 10))
        #####
        self.nodeTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.nodeTagLineEdit.setMaximumWidth(50)
        self.nodeTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.nodeTagLineEdit.setText(str([1]))
        nodeGroupHBox.addWidget(self.nodeTagLineEdit)
        ###
        resTypeLabel = QLabel("respType")
        resTypeLabel.setFont(QFont('Times', 10))
        nodeGroupHBox.addWidget(resTypeLabel)
        self.qcbox_NodeResType = QComboBox()
        self.qcbox_NodeResType.setFixedHeight(26)
        self.qcbox_NodeResType.addItems(['disp','vel','accel','reaction'])
        nodeGroupHBox.addWidget(self.qcbox_NodeResType)
        ###
        dofLabel = QLabel("DOF")
        dofLabel.setFont(QFont('Times', 10))
        nodeGroupHBox.addWidget(dofLabel)
        self.qcbox_DOF = QComboBox()
        self.qcbox_DOF.setFixedHeight(26)
        self.qcbox_DOF.addItems(['1','2','3'])
        nodeGroupHBox.addWidget(self.qcbox_DOF)
        ###
        nodePlotButton = QPushButton("Plot")
        nodePlotButton.clicked.connect(self.nodePlotButtonSlot)
        nodePlotButton.setFont(QFont('Times', 10))
        nodeGroupHBox.addWidget(nodePlotButton)
        ###
        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        nodeGroupHBox.addItem(hSpacer)
        eleTrussGroupHBox = QHBoxLayout()
        trussEleGroupBox.setLayout(eleTrussGroupHBox)
        trussEleTagLabel = QLabel("eleTag")
        eleTrussGroupHBox.addWidget(trussEleTagLabel)
        trussEleTagLabel.setFont(QFont('Times', 10))

        self.trussEleTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.trussEleTagLineEdit.setMaximumWidth(50)
        self.trussEleTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.trussEleTagLineEdit.setText(str([1]))
        eleTrussGroupHBox.addWidget(self.trussEleTagLineEdit)

        trussEleResTypeLabel = QLabel("respType")
        trussEleResTypeLabel.setFont(QFont('Times', 10))
        eleTrussGroupHBox.addWidget(trussEleResTypeLabel)
        self.qcbox_trussEleResType = QComboBox()
        self.qcbox_trussEleResType.setFixedHeight(26)
        self.qcbox_trussEleResType.addItems(['axialForce', 'axialDeform'])
        eleTrussGroupHBox.addWidget(self.qcbox_trussEleResType)

        trussElePlotButton = QPushButton("Plot")
        trussElePlotButton.clicked.connect(self.trussElePlotButtonSlot)
        trussElePlotButton.setFont(QFont('Times', 10))
        eleTrussGroupHBox.addWidget(trussElePlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        eleTrussGroupHBox.addItem(hSpacer)
        zeroEleGroupHBox = QHBoxLayout()
        zeroEleGroupBox.setLayout(zeroEleGroupHBox)
        zeroEleTagLabel = QLabel("zeroEleTag")
        zeroEleGroupHBox.addWidget(zeroEleTagLabel)
        zeroEleTagLabel.setFont(QFont('Times', 10))

        self.zeroEleTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.zeroEleTagLineEdit.setMaximumWidth(50)
        self.zeroEleTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.zeroEleTagLineEdit.setText(str([1]))
        zeroEleGroupHBox.addWidget(self.zeroEleTagLineEdit)

        zeroEleResTypeLabel = QLabel("respType")
        zeroEleResTypeLabel.setFont(QFont('Times', 10))
        zeroEleGroupHBox.addWidget(zeroEleResTypeLabel)
        self.qcbox_zeroEleResType = QComboBox()
        self.qcbox_zeroEleResType.setFixedHeight(26)
        self.qcbox_zeroEleResType.addItems(['localForce','deformation'])
        zeroEleGroupHBox.addWidget(self.qcbox_zeroEleResType)

        zeroEledofLabel = QLabel("DOF")
        zeroEledofLabel.setFont(QFont('Times', 10))
        zeroEleGroupHBox.addWidget(zeroEledofLabel)
        self.qcbox_zeroEleDOF = QComboBox()
        self.qcbox_zeroEleDOF.setFixedHeight(26)
        self.qcbox_zeroEleDOF.addItems(['1', '2', '3'])
        zeroEleGroupHBox.addWidget(self.qcbox_zeroEleDOF)

        zeroElePlotButton = QPushButton("Plot")
        zeroElePlotButton.clicked.connect(self.zeroElePlotButtonSlot)
        zeroElePlotButton.setFont(QFont('Times', 10))
        zeroEleGroupHBox.addWidget(zeroElePlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        zeroEleGroupHBox.addItem(hSpacer)
        nonEleSectGroupHBox = QHBoxLayout()
        nonEleSectGroupBox.setLayout(nonEleSectGroupHBox)
        nonEleSectTagLabel = QLabel("sectEleTag")
        nonEleSectGroupHBox.addWidget(nonEleSectTagLabel)
        nonEleSectTagLabel.setFont(QFont('Times', 10))

        self.nonEleSectTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.nonEleSectTagLineEdit.setMaximumWidth(50)
        self.nonEleSectTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.nonEleSectTagLineEdit.setText(str([1]))
        nonEleSectGroupHBox.addWidget(self.nonEleSectTagLineEdit)

        nonEleSectResTypeLabel = QLabel("respType")
        nonEleSectResTypeLabel.setFont(QFont('Times', 10))
        nonEleSectGroupHBox.addWidget(nonEleSectResTypeLabel)
        self.qcbox_nonEleSectResType = QComboBox()
        self.qcbox_nonEleSectResType.setFixedHeight(26)
        self.qcbox_nonEleSectResType.addItems(['sectionForce','sectionDeformation'])
        nonEleSectGroupHBox.addWidget(self.qcbox_nonEleSectResType)

        nonEleSectdofLabel = QLabel("DOF")
        nonEleSectdofLabel.setFont(QFont('Times', 10))
        nonEleSectGroupHBox.addWidget(nonEleSectdofLabel)
        self.qcbox_nonEleSectDOF = QComboBox()
        self.qcbox_nonEleSectDOF.setFixedHeight(26)
        self.qcbox_nonEleSectDOF.addItems(['1', '2', '3','4'])
        nonEleSectGroupHBox.addWidget(self.qcbox_nonEleSectDOF)

        nonEleSectPlotButton = QPushButton("Plot")
        nonEleSectPlotButton.clicked.connect(self.nonEleSectPlotButtonSlot)
        nonEleSectPlotButton.setFont(QFont('Times', 10))
        nonEleSectGroupHBox.addWidget(nonEleSectPlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        nonEleSectGroupHBox.addItem(hSpacer)
        nonZeroEleGroupHBox = QHBoxLayout()
        nonZeroEleGroupBox.setLayout(nonZeroEleGroupHBox)
        nonZeroEleTagLabel = QLabel("EleTag")
        nonZeroEleGroupHBox.addWidget(nonZeroEleTagLabel)
        nonZeroEleTagLabel.setFont(QFont('Times', 10))

        self.nonZeroEleTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.nonZeroEleTagLineEdit.setMaximumWidth(50)
        self.nonZeroEleTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.nonZeroEleTagLineEdit.setText(str([1]))
        nonZeroEleGroupHBox.addWidget(self.nonZeroEleTagLineEdit)

        nonZeroEleResTypeLabel = QLabel("respType")
        nonZeroEleResTypeLabel.setFont(QFont('Times', 10))
        nonZeroEleGroupHBox.addWidget(nonZeroEleResTypeLabel)
        self.qcbox_nonZeroEleResType = QComboBox()
        self.qcbox_nonZeroEleResType.setFixedHeight(26)
        self.qcbox_nonZeroEleResType.addItems(['localForce'])
        nonZeroEleGroupHBox.addWidget(self.qcbox_nonZeroEleResType)

        nonZeroEleEndLabel = QLabel("End")
        nonZeroEleEndLabel.setFont(QFont('Times', 10))
        nonZeroEleGroupHBox.addWidget(nonZeroEleEndLabel)
        self.qcbox_nonZeroEleEnd = QComboBox()
        self.qcbox_nonZeroEleEnd.setFixedHeight(26)
        self.qcbox_nonZeroEleEnd.addItems(['I', 'J'])
        nonZeroEleGroupHBox.addWidget(self.qcbox_nonZeroEleEnd)

        nonZeroEledofLabel = QLabel("DOF")
        nonZeroEledofLabel.setFont(QFont('Times', 10))
        nonZeroEleGroupHBox.addWidget(nonZeroEledofLabel)
        self.qcbox_nonZeroEleDOF = QComboBox()
        self.qcbox_nonZeroEleDOF.setFixedHeight(26)
        self.qcbox_nonZeroEleDOF.addItems(['1', '2', '3', '4','5','6'])
        nonZeroEleGroupHBox.addWidget(self.qcbox_nonZeroEleDOF)

        nonZeroElePlotButton = QPushButton("Plot")
        nonZeroElePlotButton.clicked.connect(self.nonZeroElePlotButtonSlot)
        nonZeroElePlotButton.setFont(QFont('Times', 10))
        nonZeroEleGroupHBox.addWidget(nonZeroElePlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        nonZeroEleGroupHBox.addItem(hSpacer)
        trussEleHysterGroupHBox = QHBoxLayout()
        trussEleHysteGroupBox.setLayout(trussEleHysterGroupHBox)
        trussEleHysterTagLabel = QLabel("eleTag")
        trussEleHysterGroupHBox.addWidget(trussEleHysterTagLabel)
        trussEleHysterTagLabel.setFont(QFont('Times', 10))

        self.trussEleHysterTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.trussEleHysterTagLineEdit.setMaximumWidth(50)
        self.trussEleHysterTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.trussEleHysterTagLineEdit.setText(str([1]))
        trussEleHysterGroupHBox.addWidget(self.trussEleHysterTagLineEdit)

        trussEleHysterPlotButton = QPushButton("Plot")
        trussEleHysterPlotButton.clicked.connect(self.trussEleHysterPlotButtonSlot)
        trussEleHysterPlotButton.setFont(QFont('Times', 10))
        trussEleHysterGroupHBox.addWidget(trussEleHysterPlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        trussEleHysterGroupHBox.addItem(hSpacer)
        zeroEleHysterGroupHBox = QHBoxLayout()
        zeroEleHysteGroupBox.setLayout(zeroEleHysterGroupHBox)
        zeroEleHysterTagLabel = QLabel("zeroEleTag")
        zeroEleHysterGroupHBox.addWidget(zeroEleHysterTagLabel)
        zeroEleHysterTagLabel.setFont(QFont('Times', 10))

        self.zeroEleHysterTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.zeroEleHysterTagLineEdit.setMaximumWidth(50)
        self.zeroEleHysterTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.zeroEleHysterTagLineEdit.setText(str([1]))
        zeroEleHysterGroupHBox.addWidget(self.zeroEleHysterTagLineEdit)

        zeroEleHysterdofLabel = QLabel("DOF")
        zeroEleHysterdofLabel.setFont(QFont('Times', 10))
        zeroEleHysterGroupHBox.addWidget(zeroEleHysterdofLabel)
        self.qcbox_zeroEleHysterDOF = QComboBox()
        self.qcbox_zeroEleHysterDOF.setFixedHeight(26)
        self.qcbox_zeroEleHysterDOF.addItems(['1', '2', '3'])
        zeroEleHysterGroupHBox.addWidget(self.qcbox_zeroEleHysterDOF)

        zeroEleHysterPlotButton = QPushButton("Plot")
        zeroEleHysterPlotButton.clicked.connect(self.zeroEleHysterPlotButtonSlot)
        zeroEleHysterPlotButton.setFont(QFont('Times', 10))
        zeroEleHysterGroupHBox.addWidget(zeroEleHysterPlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        zeroEleHysterGroupHBox.addItem(hSpacer)
        sectEleHysterGroupHBox = QHBoxLayout()
        sectEleHysteGroupBox.setLayout(sectEleHysterGroupHBox)
        sectEleHysterTagLabel = QLabel("sectEleTag")
        sectEleHysterGroupHBox.addWidget(sectEleHysterTagLabel)
        sectEleHysterTagLabel.setFont(QFont('Times', 10))

        self.sectEleHysterTagLineEdit = QLineEdit(toolTip="List input like[1] or [1,4,7,9]")
        self.sectEleHysterTagLineEdit.setMaximumWidth(50)
        self.sectEleHysterTagLineEdit.setAlignment(Qt.AlignHCenter)
        self.sectEleHysterTagLineEdit.setText(str([1]))
        sectEleHysterGroupHBox.addWidget(self.sectEleHysterTagLineEdit)

        sectEleHysterdofLabel = QLabel("DOF")
        sectEleHysterdofLabel.setFont(QFont('Times', 10))
        sectEleHysterGroupHBox.addWidget(sectEleHysterdofLabel)
        self.qcbox_sectEleHysterDOF = QComboBox()
        self.qcbox_sectEleHysterDOF.setFixedHeight(26)
        self.qcbox_sectEleHysterDOF.addItems(['1', '2', '3', '4'])
        sectEleHysterGroupHBox.addWidget(self.qcbox_sectEleHysterDOF)

        sectEleHysterPlotButton = QPushButton("Plot")
        sectEleHysterPlotButton.clicked.connect(self.sectEleHysterPlotButtonSlot)
        sectEleHysterPlotButton.setFont(QFont('Times', 10))
        sectEleHysterGroupHBox.addWidget(sectEleHysterPlotButton)

        hSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        sectEleHysterGroupHBox.addItem(hSpacer)
        #############################################
        #############################################
        vSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        v2_1Box.addItem(vSpacer)
        windowWidth = self.width()
        self.splitterH.setSizes([int(0.95 * windowWidth), int(0.05 * windowWidth)])
        mainFrame = QFrame()
        vBox = QVBoxLayout()
        vBox.addWidget(self.splitterH)
        mainFrame.setLayout(vBox)
        self.setCentralWidget(mainFrame)
    def plotSetting(self):
        """---Setting matplotlib---"""
        self.ax.clear()
        self.ax.grid(True, color='grey', which="both", linewidth=0.2, linestyle='dashdot')
        self.ax.spines['top'].set_linewidth(0.2)
        self.ax.spines['bottom'].set_linewidth(0.2)
        self.ax.spines['right'].set_linewidth(0.2)
        self.ax.spines['left'].set_linewidth(0.2)

    def nodePlotButtonSlot(self):
        """---slot function for node time history response plot---"""
        nodeTagList = eval(self.nodeTagLineEdit.text())
        legendList=[str(each) for each in nodeTagList]
        resType=self.qcbox_NodeResType.currentText()
        nodeDOF=int(self.qcbox_DOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('time (s)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('node-' + resType, font='Times New Roman', fontsize=15)
        for eachNode in nodeTagList:
            timesList, resList = dbInstance.getNodeTimeHistory(eachNode, resType, nodeDOF)
            self.ax.plot(timesList, resList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def trussElePlotButtonSlot(self):
        """---slot function for truss element history response plot---"""
        trussEleTagList = eval(self.trussEleTagLineEdit.text())
        legendList = [str(each) for each in trussEleTagList]
        resType = self.qcbox_trussEleResType.currentText()
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('time (s)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('trussEle-' + resType, font='Times New Roman', fontsize=15)
        for eachTrussEle in trussEleTagList:
            timesList, resList = dbInstance.getTrussEleResponseTimeHistory(eachTrussEle,resType)
            self.ax.plot(timesList, resList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def zeroElePlotButtonSlot(self):
        """---slot function for zerolength element time history response plot---"""
        zeroEleTagList = eval(self.zeroEleTagLineEdit.text())
        legendList=[str(each) for each in zeroEleTagList]
        resType=self.qcbox_zeroEleResType.currentText()
        eleDOF=int(self.qcbox_zeroEleDOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('time (s)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('zeroEle-' + resType, font='Times New Roman', fontsize=15)
        for eachEle in zeroEleTagList:
            timesList, resList = dbInstance.getZeroEleResponseTimeHistory(eachEle,resType,eleDOF)
            self.ax.plot(timesList, resList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def nonEleSectPlotButtonSlot(self):
        """---slot function for nonlinear element section time history response plot---"""
        nonEleSectTagList = eval(self.nonEleSectTagLineEdit.text())
        legendList = [str(each) for each in nonEleSectTagList]
        resType = self.qcbox_nonEleSectResType.currentText()
        eleDOF = int(self.qcbox_nonEleSectDOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('time (s)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('nonEleSect-' + resType, font='Times New Roman', fontsize=15)
        for eachEle in nonEleSectTagList:
            timesList, resList = dbInstance.getNonEleSectResponseTimeHistory(eachEle,resType,eleDOF)
            self.ax.plot(timesList, resList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def nonZeroElePlotButtonSlot(self):
        """---slot function for non-zerolength element time history response plot---"""
        nonZeroEleTagList = eval(self.nonZeroEleTagLineEdit.text())
        legendList = [str(each) for each in nonZeroEleTagList]
        resType = self.qcbox_nonZeroEleResType.currentText()
        End=self.qcbox_nonZeroEleEnd.currentText()
        eleDOF = int(self.qcbox_nonZeroEleDOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('time (s)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('nonZeroEle-' + resType, font='Times New Roman', fontsize=15)
        for eachEle in nonZeroEleTagList:
            timesList, resList = dbInstance.getNonZeroEleResponseTimeHistory(eachEle,resType,End,eleDOF)
            self.ax.plot(timesList, resList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def trussEleHysterPlotButtonSlot(self):
        """---slot function for truss element hysteretic response plot---"""
        trussEleHysterTagList = eval(self.trussEleHysterTagLineEdit.text())
        legendList = [str(each) for each in trussEleHysterTagList]
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('disp', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('force', font='Times New Roman', fontsize=15)
        for eachTrussEle in trussEleHysterTagList:
            _, dispList = dbInstance.getTrussEleResponseTimeHistory(eachTrussEle,'axialDeform')
            _, forceList = dbInstance.getTrussEleResponseTimeHistory(eachTrussEle, 'axialForce')
            self.ax.plot(dispList,forceList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def zeroEleHysterPlotButtonSlot(self):
        """---slot function for zerolength element hysteretic response plot---"""
        zeroEleHysterTagList = eval(self.zeroEleHysterTagLineEdit.text())
        legendList = [str(each) for each in zeroEleHysterTagList]
        eleDOF = int(self.qcbox_zeroEleHysterDOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('disp', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('force', font='Times New Roman', fontsize=15)
        for eachEle in zeroEleHysterTagList:
            print(eachEle,eleDOF)
            _, dispList = dbInstance.getZeroEleResponseTimeHistory(eachEle,'deformation', eleDOF)
            _, forceList = dbInstance.getZeroEleResponseTimeHistory(eachEle, 'localForce', eleDOF)
            self.ax.plot(dispList, forceList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()

    def sectEleHysterPlotButtonSlot(self):
        """---slot function for nonlinear element section hysteretic response plot---"""
        sectEleHysterTagList = eval(self.sectEleHysterTagLineEdit.text())
        legendList = [str(each) for each in sectEleHysterTagList]
        eleDOF = int(self.qcbox_sectEleHysterDOF.currentText())
        dbInstance = SqliteDB(self.dbPath)
        self.plotSetting()
        self.ax.set_xlabel('curvature (strain)', font='Times New Roman', fontsize=18)
        self.ax.set_ylabel('moment (force)', font='Times New Roman', fontsize=15)
        for eachEle in sectEleHysterTagList:
            _, curvatureList = dbInstance.getNonEleSectResponseTimeHistory(eachEle,'sectionDeformation',eleDOF)
            _, momentList = dbInstance.getNonEleSectResponseTimeHistory(eachEle, 'sectionForce', eleDOF)
            self.ax.plot(curvatureList,momentList, linewidth=0.8)
        self.ax.legend(labels=legendList)
        self.figCanvas.draw()
########################################################################################################################
########################################################################################################################
class DefaultSetting():
    """---default setting class---"""
    def __init__(self,Window):
        """---window is the basic panel class---"""
        self.mainWindow=Window
        self.backGroundColorSetting()

    def backGroundColorSetting(self):
        """---background color setting---"""
        backGroundColor = DefaultSet.getValue(tableName="backGroundColorTable",
                                              tagName="backGroundColor")
        self.mainWindow.plotter.set_background(backGroundColor)
########################################################################################################################
########################################################################################################################
if __name__ == '__main__':
    app=QApplication(sys.argv)
    window = MainWindow()
    DefaultSetting(window)
    window.show()
    exit_code=app.exec_()
    sys.exit(exit_code)