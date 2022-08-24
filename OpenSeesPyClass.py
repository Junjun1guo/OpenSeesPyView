#-*-coding: UTF-8-*-
#####Units: Length-m, Force-kN, mass-ton, Stress-kpa(10e-3MPa), g=9.81m/s2
#####Units: Length-mm, Force-N, mass-ton, Stress-Mpa, g=9810mm/s2 pho=ton/mm3
########################################################################################################################
#  Author: Junjun Guo,Tongji University. https://github.com/Junjun1guo
#  E-mail: guojj@tongji.edu.cn/guojj_ce@163.com
#  Environemet: Successfully executed in python 3.8
#  Date: 2022-01-29
########################################################################################################################
########################---import modules---#################################
import os
import numpy as np
import openseespy.opensees as ops
import time
import records
from SqliteDB import SqliteDB  ##sqlite database to store opensees results
import matplotlib.pyplot as plt
########################################################################################################################
########################################################################################################################
class OpenSeesPyClass():
    """A class for openSeesPy script"""
    def __init__(self,caseNumber,waveNumber):
        """
        Initialize the class
        ------------------------------------------
        Inputs:
            caseNumber(int)-the case number
            waveNumber(int)-the ground motion number
        """
        self.caseNumber=caseNumber
        self.waveNumber=waveNumber
        self.nodeSetNameList=[]
        self.eleSetNameList=[]
        self.modalNameList=[]
        self.EleLocalCoordSysSetNameList=[]
        self.localTransfNameList=[]
        self.materialNumberDict={}
        self.dbPath = "resultsDB_"+str(self.caseNumber)+str("_")+str(self.waveNumber)+".db"
        self.saveInstance = SqliteDB(self.dbPath)
        SqliteDB.initDB(self.dbPath)

    def model_ndm(self):
        """Set the default model dimensions and number of dofs."""
        ops.model('basic', '-ndm', 3, '-ndf', 6) ###for 3D model

    def node_create(self,nodeList,tipsString=""):
        """
        Create a OpenSees node
        ------------------------------------------
        Inputs:
            nodeList(list)-eg.[[nodeTag,xCoord,yCoord,ZCoord,nodeMass],[],...]
            tipsString(str)-the string for identifying the nodes set
        """
        print(tipsString+' constructing start...')
        saveList=[]
        for each in nodeList:
            nodeTageValue = int(each[0])
            xCoordValue = float(each[1])
            yCoordValue = float(each[2])
            zCoordValue = float(each[3])
            nodeMassValue = float(each[4])
            ops.node(nodeTageValue, xCoordValue, yCoordValue, zCoordValue, '-mass', nodeMassValue, nodeMassValue,
                 nodeMassValue, 0.0, 0.0, 0.0)
            coords=ops.nodeCoord(nodeTageValue)
            saveList.append([nodeTageValue]+coords)
        print(tipsString + ' constructing finish...')
        self.nodeSetNameList.append(tipsString+"_node")
        self.saveInstance.saveNodes(nodesSaveName=tipsString+"_node",nodeList=saveList)

    def cable_material(self,cableMateriallist,cableYieldStress=0.0,tipsString=""):
        """
        Use elasticPP material simulate prestressed cable
        ------------------------------------------
        Inputs:
            cableMateriallist(list)-eg.[[cableMatTag,cableE,cablePreStress],[]]
            cableYieldStress(float,kpa)-the yield stress for the cable
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        for each in cableMateriallist:
            cableMatTag = int(each[0])
            cableEValue = float(each[1])
            preStrValue = float(each[2])
            eps0Value = -preStrValue / float(cableEValue)
            epsyNValue = 0.0
            epsyPValue = cableYieldStress/ float(cableEValue) + eps0Value
            ops.uniaxialMaterial('ElasticPP', cableMatTag, cableEValue, epsyPValue, epsyNValue, eps0Value)
        print(tipsString + ' constructing finish...')

    def ele_truss(self,eleList,tipsString=""):
        """
        Construct a truss element
        ------------------------------------------
        Inputs:
            eleList(list)-eg. [[eleTag,NodeI,nodeJ,Area,matTag],[],...]
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        saveList=[]
        for each in eleList:
            EleTag = int(each[0])
            NodeI = int(each[1])
            NodeJ = int(each[2])
            A = float(each[3])
            MatTag = int(each[4])
            ops.element('Truss', EleTag, NodeI, NodeJ, A, MatTag)
            eleNodes = ops.eleNodes(EleTag)
            saveList.append([EleTag] + eleNodes)
        self.eleSetNameList.append(tipsString+"_ele")
        self.saveInstance.saveEles(elesSaveName=tipsString+"_ele", elesList=saveList)
        print(tipsString + ' constructing finish...')

    def geomTransf_PDelta(self,geomTransfList,tipsString=""):
        """
        Used to construct the P-Delta Coordinate Transformation (PDeltaCrdTransf),i.e, the gloabal coordinate values
        for local Z axis
        ------------------------------------------
        Inputs:
            geomTransfList(list)-eg.[[TransfTag,localZXCoord,localZYCoord,localZZCoord],[],...]
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        saveGeomfList=[]
        for each in geomTransfList:
            TransfTag = int(each[0])
            localZXCoord = float(each[1])
            localZYCoord = float(each[2])
            localZZCoord = float(each[3])
            ops.geomTransf('PDelta', TransfTag,localZXCoord,localZYCoord,localZZCoord)
            saveGeomfList.append([TransfTag,localZXCoord,localZYCoord,localZZCoord])
        self.localTransfNameList.append(tipsString + "_geomTransf")
        self.saveInstance.saveGeomTransf(geomTransfSaveName=tipsString + "_geomTransf",geomfList=saveGeomfList)

        print(tipsString + ' constructing finish...')

    def ele_elasticBeamColum(self,eleList,tipsString=""):
        """
        Construct an elasticBeamColumn element object
        ------------------------------------------
        Inputs:
            eleList(list)-eg.[[eleTag,nodeI,nodeJ,A,E,G,J,Iy,Iz,Transf],[],...]
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        saveList=[]
        EleLocalCoordSys=[]
        for each in eleList:
            EleTag = int(each[0])
            NodeI = int(each[1])
            NodeJ = int(each[2])
            A = float(each[3])
            E = float(each[4])
            G = float(each[5])
            J = float(each[6])
            Iy = float(each[7])
            Iz = float(each[8])
            Transf = int(each[9])
            ops.element('elasticBeamColumn', EleTag, NodeI, NodeJ, A,E,G,J,Iy,Iz,Transf)
            eleNodes = ops.eleNodes(EleTag)
            saveList.append([EleTag] + eleNodes)
            EleLocalCoordSys.append(['realEle',NodeI,NodeJ,Transf])
        self.eleSetNameList.append(tipsString+"_ele")
        self.EleLocalCoordSysSetNameList.append(tipsString+"_eleLocCordSys")
        self.saveInstance.saveEles(elesSaveName=tipsString+"_ele", elesList=saveList)
        self.saveInstance.saveEleLocalCoordSys(SaveName=tipsString+"_eleLocCordSys",EleLocalCoordSys=EleLocalCoordSys)

        print(tipsString + ' constructing finish...')

    def materialReNumber(self,materialName):
        """
        Register a material name in the domain and return a unique number of the mateiral
        """
        if materialName not in self.materialNumberDict.keys():
            self.materialNumberDict[materialName]=len(self.materialNumberDict.keys())+10000
        else:
            print(f'the name {materialName} has been used!')
        return self.materialNumberDict[materialName]

    def fiber_section(self,eleTag,fiberList,matTagList,GJValue=1.0e10,tipsString=""):
        """
        Construct fiber seciton
        ------------------------------------------
        Inputs:
            eleTag(int)-the number of fiber section
            fiberList(list)-the fiber information list, eg. [[[yloc0_0,zloc0_0,A0_0],[yloc1_0,zloc01_0,A1_0]],
                [yloc0_1,zloc0_1,A0_1],[yloc1_1,zloc01_1,A1_1]]
            matTagList(list)-material number list corresponding to each element in fiberList,eg.[1,2]
            GJValue-(float)-linear-elastic torsional stiffness assigned to the section (default value takes 1.0e10)
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        ops.section('Fiber', int(eleTag), '-GJ', GJValue)
        [ops.fiber(eachItem[0], eachItem[1], eachItem[2], matTagList[i1])
         for i1 in range(len(fiberList)) for eachItem in fiberList[i1]]
        print(tipsString + ' constructing finish...')

    def ele_nonlinearBeamColumn(self,nonlinearEleList,integrationPoint=5,tipsString=''):
        """
        Create a nonlinearBeamColumn element.
        ------------------------------------------
        Inputs:
            nonlinearEleList(list)-eg.[[eleTag,nodeI,nodeJ,geomTransf,section],[],...]
            integrationPoint(int)-number of integration points.
            tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        self.intePointNum=integrationPoint
        saveList=[]
        EleLocalCoordSys = []
        for each in nonlinearEleList:
            EleTag = int(each[0])
            EleNodeI = int(each[1])
            EleNodeJ = int(each[2])
            EleGeomTransf = int(each[3])
            EleSection = int(each[4])
            ops.element('nonlinearBeamColumn', EleTag, EleNodeI, EleNodeJ, integrationPoint,
                    EleSection, EleGeomTransf)
            eleNodes = ops.eleNodes(EleTag)
            saveList.append([EleTag] + eleNodes)
            EleLocalCoordSys.append(['realEle', EleNodeI,EleNodeJ, EleGeomTransf])
        self.eleSetNameList.append(tipsString+"_ele")
        self.saveInstance.saveEles(elesSaveName=tipsString+"_ele", elesList=saveList)
        self.EleLocalCoordSysSetNameList.append(tipsString + "_eleLocCordSys")
        self.saveInstance.saveEleLocalCoordSys(SaveName=tipsString + "_eleLocCordSys",
                                               EleLocalCoordSys=EleLocalCoordSys)
        print(tipsString + ' constructing finish...')

    def fix_complete(self,fixList,tipsString=''):
        """
        fix node in all DOF
        -------------------------------------
        Inputs:
            fixList(list)-eg.[nodeTag1,nodeTag2,...]

        """
        print(tipsString + ' constructing start...')
        for each in fixList:
            ops.fix(int(each), 1, 1, 1, 1, 1, 1)
        print(tipsString + ' constructing finish...')

    def gravity_load(self,nodesList,tipsString=""):
        """
        Apply gravity load to associated nodes
        ------------------------------------------
        nodesList(list)-eg.[[[node1Tag,node1Mass],[],...],[],...]
        """
        print(tipsString + ' constructing start...')
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        for each in nodesList:
            ops.load(int(each[0]), 0.0, 0.0, -each[1] * 9.81, 0.0, 0.0, 0.0)
        print(tipsString + ' constructing finish...')

    def analysis_gravity(self,tipsString='',recordList=None):
        """
        Static gravity load analysis
        ------------------------------------------
        totalStep(int)-Number of analysis steps to perform
        tipsString(str)-print information on console
        """
        print(tipsString + ' constructing start...')
        totalStep = 1
        ops.system('UmfPack')
        ops.constraints('Transformation')
        ops.numberer('RCM')
        ops.test('NormDispIncr', 1.0e-8, 2000)
        ops.algorithm('KrylovNewton')
        ops.integrator('LoadControl',1.0/float(totalStep))
        ops.analysis('Static')
        ops.analyze(int(totalStep))
        ops.loadConst('-time', 0.0)
        #######################################################
        if recordList!=None:
            nodeDict={}
            trussEleResponseDict={}
            zeroEleResponseDict={}
            zeroEleDirectionDict={}
            nonEleSectResponsesDict={}
            nonEleSectNumberDict={}
            nonZeroEleResponsesDict={}
            for each in recordList:
                if each[0]=='node':
                    nodeIdenty, resType,nodeTags= each[0], each[1], each[2]
                    nodeItemDict={(nodeIdenty+'_'+resType+'_'+str(eachNode)):[] for eachNode in nodeTags}
                    nodeDict={**nodeDict,**nodeItemDict}##Merge two dicts
                elif each[0]=='trussEle':
                    responseType,eleTags =each[1],each[2]
                    eleItemDict={('trussEle_'+responseType+'_'+str(eachEle)):[] for eachEle in eleTags}
                    trussEleResponseDict = {**trussEleResponseDict, **eleItemDict}  ##Merge two dicts
                elif each[0]=='zeroEle':
                    responseType, directions,eleTags = each[1], each[2],each[3]
                    eleItemDict = {('zeroEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    zeroEleResponseDict = {**zeroEleResponseDict, **eleItemDict}  ##Merge two dicts
                    eleDirectDict = {('zeroEle_' + responseType + '_' + str(eachEle)):directions for eachEle in eleTags}
                    zeroEleDirectionDict = {**zeroEleDirectionDict, **eleDirectDict}  ##Merge two dicts
                elif each[0]=='nonEleSection':
                    responseType,sectNum,eleTags=each[1],each[2],each[3]
                    eleItemDict = {('nonEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    nonEleSectResponsesDict = {**nonEleSectResponsesDict, **eleItemDict}  ##Merge two dicts
                    sectNumDict = {('nonEle_' + responseType + '_' + str(eachEle)): sectNum for eachEle in eleTags}
                    nonEleSectNumberDict = {**nonEleSectNumberDict, **sectNumDict}  ##Merge two dicts
                elif each[0]=='nonZeroEle':
                    responseType,eleTags = each[1], each[2]
                    eleItemDict = {('nonZeroEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    nonZeroEleResponsesDict = {**nonZeroEleResponsesDict, **eleItemDict}  ##Merge two dicts
        ####################---recorderProcess---###########
        if recordList != None:
            if nodeDict:
                nodeKeys = nodeDict.keys()
                nodeResNameDict = {'disp': 'nodeDisp', 'vel': 'nodeVel', 'accel': 'nodeAccel',
                                   'reaction': 'nodeReaction'}
                [[resType := eachkey.split('_')[1], nodeTag := eachkey.split('_')[2],
                  tempValue1 := [0.0],
                  tempValue2 := eval(f"ops.{nodeResNameDict[resType]}({nodeTag})"),
                  tempValue3 := [round(tempValue2[i1], 6) for i1 in range(3)],
                  tempValue := tempValue1 + tempValue3,
                  nodeDict['node_' + resType + '_' + str(nodeTag)].append(tempValue)] for eachkey in
                 nodeKeys]  ##海象运算符加列表解析
                [[resType := eachkey.split("_")[1], nodeTag := eachkey.split("_")[2],
                  saveValueList := nodeDict['node_' + resType + '_' + str(nodeTag)],
                  self.saveInstance.saveNodeTimeHistory(nodeSaveName=eachkey,
                nodeHistoryList=saveValueList)] for eachkey in nodeKeys]
            if trussEleResponseDict:
                eleKeys = trussEleResponseDict.keys()
                eleResNameDict = {'axialForce': 'basicForce', 'axialDeform': 'basicDeformation'}
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  tempValue1 := [0.0],
                  tempValue2 := [round(eval(f"ops.{eleResNameDict[resType]}({eleTag})[0]"), 3)],
                  tempValue := tempValue1 + tempValue2,
                  trussEleResponseDict['trussEle_' + resType + '_' + str(eleTag)].append(tempValue)] for
                 eachkey in eleKeys]
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  saveValueList := trussEleResponseDict['trussEle_' + resType + '_' + str(eleTag)],
                  self.saveInstance.saveTrussEleResponseTimeHistory(eleSaveName=eachkey,
                eleHistoryList=saveValueList)] for eachkey in eleKeys]
            if zeroEleResponseDict:
                eleKeys = zeroEleResponseDict.keys()
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  tempValue1 := [0.0],
                  tempValue2 := eval(f"ops.eleResponse({eleTag},'{resType}')"),
                  tempValue3 := [[round(each, 3) for each in tempValue2]],
                  tempValue := tempValue1 + tempValue3 + [zeroEleDirectionDict[eachkey]],
                  zeroEleResponseDict['zeroEle_' + resType + '_' + str(eleTag)].append(tempValue)] for
                 eachkey in eleKeys]  ##海象操作符
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  saveValueList := zeroEleResponseDict['zeroEle_' + resType + '_' + str(eleTag)],
                  self.saveInstance.saveZeroEleResponseTimeHistory(eleSaveName=eachkey,
                eleHistoryList=saveValueList)] for eachkey in eleKeys]
            if nonEleSectResponsesDict:
                eleKeys = nonEleSectResponsesDict.keys()
                digitNumDict = {'sectionForce': 3, 'sectionDeformation': 10}
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  tempValue := [0.0] + [
                      round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},1)"),
                            digitNumDict[resType]),
                      round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},2)"),
                            digitNumDict[resType]),
                      round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},3)"),
                            digitNumDict[resType]),
                      round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},4)")),
                      digitNumDict[resType]],
                  nonEleSectResponsesDict['nonEle_' + resType + '_' + str(eleTag)].append(tempValue)] for
                 eachkey in eleKeys]
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  saveValueList := nonEleSectResponsesDict['nonEle_' + resType + '_' + str(eleTag)],
                  self.saveInstance.saveNonEleSectResponseTimeHistory(eleSaveName=eachkey,
                eleHistoryList=saveValueList)] for eachkey in eleKeys]
            if nonZeroEleResponsesDict:
                eleKeys = nonZeroEleResponsesDict.keys()
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  tempValue1 := [0.0],
                  tempValue2 := eval(f"ops.eleResponse({eleTag},'{resType}')"),
                  tempValue3 := [round(each, 3) for each in tempValue2],
                  tempValue := tempValue1 + tempValue3,
                  nonZeroEleResponsesDict[eachkey].append(tempValue)] for eachkey in eleKeys]
                [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],
                  saveValueList := nonZeroEleResponsesDict[eachkey],
                  self.saveInstance.saveNonZeroEleResponseTimeHistory(eleSaveName=eachkey,
                    eleHistoryList=saveValueList)] for eachkey in eleKeys]
        ######################################################
        ######################################################
        print(tipsString + ' constructing finish...')

    def analysis_modal(self,numModes=10,tipsString=''):
        """
        Modal analysis
        ------------------------------------------
        numModes(int)-number of eigenvalues required
        """
        print(tipsString + ' constructing start...')
        eigenValues = ops.eigen(numModes)
        allNodesTag=ops.getNodeTags()
        self.modalNameList.append(tipsString+'_mode')
        for eachMode in range(numModes):
            saveList = []
            for eachNode in allNodesTag:
                nodeEigenValue = ops.nodeEigenvector(eachNode, int(eachMode + 1))
                saveList.append([eachNode] + nodeEigenValue)
            self.saveInstance.saveModes(modesName=tipsString+'_mode'+'_'+str(eachMode+1), modesList=saveList)

        savePeridList=[]
        for i1 in range(numModes):
            periodT = 2.0 * 3.1415926 / float(eigenValues[i1] ** 0.5)
            savePeridList.append([i1+1,periodT])
        self.saveInstance.savePeriod(periodList=savePeridList)
        for i2 in range(10):
            print(str(i2 + 1) + ' th period is: ' + str(savePeridList[i2]) + ' second')
        print(tipsString + ' constructing finish...')

    def _makeDirs(self,savePath):
        """
        Make directory if not exists
        ------------------------------------------
        savePath(str)-the path of the directory
        """
        if os.path.exists(savePath):
            pass
        else:
            os.makedirs(savePath)

    def recorder_node(self,savePath,nodeLists,dofLists,responseType,tipsString=''):
        """
        Records the response of a number of nodes at every converged step
        ------------------------------------------
        savePath(str)-the path of the directory,eg.'nodeDisp'
        nodeLists(list)-nodes that need record responses, eg. [1,2,3,4]
        dofLists(list)-the specified dof at the nodes whose response is requested.eg. [1,2,3]
        responseType(str)-a string indicating response required
            including:
            'disp' displacement
            'vel' velocity
            'accel' acceleration
            'incrDisp' incremental displacement
            'reaction' nodal reaction
            'eigen i' eigenvector for mode i
            'rayleighForces' damping forces
        """
        print(tipsString + ' constructing start...')
        self._makeDirs(savePath)
        fileName = savePath + '/' +str(self.caseNumber)+"_"+ str(self.waveNumber) + '.txt'
        linkstr = f"ops.recorder('Node', '-file','{fileName}', '-time', '-node',"
        for each in nodeLists:
            linkstr+=f"{each}"+f","
        linkstr+=f"'-dof',"
        for each in dofLists:
            linkstr+=f"{each}"+f","
        linkstr+=f"'{responseType}')"
        eval(linkstr)
        print(tipsString + ' constructing finish...')

    def recorder_element(self,savePath,eleList,responseTypeList,tipsString=''):
        """
        Records the response of a number of elements at every converged step
        ------------------------------------------
        savePath(str)-the path of the directory,eg.'eleForce'
        eleLists(list)-elements that need record responses, eg. [1,2,3,4]
        responseTypeList(list)-arguments which are passed to the setResponse()
            include:
            ['axialForce']-for truss element,1 column for each element
            ['section','1','force']-for nonlinear element force at integrationPoint 1, 4column for each element
            ['section', '1', 'deformation']-for nonlinear element deformation at integrationPoint 1,4column for each element
            ['localForce']-for elestic beamcolumn element and zerolength element force
            ['deformation']--for elestic beamcolumn element and zerolength element deformation
        """
        print(tipsString + ' constructing start...')
        self._makeDirs(savePath)
        fileName = savePath + '/' +str(self.caseNumber)+"_"+ str(self.waveNumber) + '.txt'
        linkstr = f"ops.recorder('Element', '-file','{fileName}', '-time', '-ele',"
        for each in eleList:
            linkstr+=f"{each}"+f","
        for i1 in range(len(responseTypeList)-1):
            linkstr += f"'{responseTypeList[i1]}'" + f","
        linkstr+=f"'{responseTypeList[-1]}'"+f")"
        eval(linkstr)
        print(tipsString + ' constructing finish...')

    def earthquake_excite(self,dampRatio,Tstart,Tend,waveLenthList,dtList,dirList,motionList,recordList=None):
        """
        Apply a uniform excitation to a model acting in a certain direction
        ------------------------------------------
        dampRatio(float)-the damping ratio for the structure,eg.0.05
        Tstart,Tend(float)-the start and end periods for calculating rayleigh damping
        waveLenthList(list)-a txt file that stores the motion lengths for each ground motion
        dtList(list)-a txt file that stores the time intervals for each ground motion
        dirList(list)-direction in which ground motion acts,eg. [1,3]
            1 corresponds to translation along the global X axis
            2 corresponds to translation along the global Y axis
            3 corresponds to translation along the global Z axis
            4 corresponds to rotation about the global X axis
            5 corresponds to rotation about the global Y axis
            6 corresponds to rotation about the global Z axis
        motionList(list)-grond motions corresponding to the dirList,eg.[acc_X,acc_Z]
        """
        w1=2.0*np.pi/float(Tstart)
        w2=2.0*np.pi/float(Tend)
        a = dampRatio * 2.0 * w1 * w2 / float(w1 + w2)
        b = dampRatio * 2 / float(w1 +w2)
        ### D=α×M＋β1×Kcurrent＋β2×Kinit＋β3×KlastCommit Longitudinal direction
        ops.rayleigh(a, 0.0, 0.0,b)
        print('rayleigh damping: ', a, b)
        ops.loadConst('-time', 0.0)
        currentLength = int(waveLenthList[self.waveNumber - 1])
        currentDt = float(dtList[self.waveNumber - 1])
        dir_L, dir_T, dir_V = 1, 2, 3
        gmFact = 9.81
        for i1 in range(len(dirList)):
            ops.timeSeries('Path', int(i1+100), '-dt', currentDt, '-filePath',motionList[i1], '-factor', gmFact)
            ops.pattern('UniformExcitation', int(i1+1000), int(dirList[i1]), '-accel', int(i1+100))
        ######################################################
        ops.wipeAnalysis()
        ops.constraints('Transformation')
        ops.numberer('RCM')
        ops.system('UmfPack')
        # ops.test('NormDispIncr', tol,maxNumIter)
        # ops.algorithm('KrylovNewton')
        # ops.integrator('Newmark', 0.5, 0.25)
        # ops.analysis('Transient')
        ######################################################
        #######################################################
        writeInterNum=500
        if recordList!=None:
            nodeDict={}
            trussEleResponseDict={}
            zeroEleResponseDict={}
            zeroEleDirectionDict={}
            nonEleSectResponsesDict={}
            nonEleSectNumberDict={}
            nonZeroEleResponsesDict={}
            for each in recordList:
                if each[0]=='node':
                    nodeIdenty, resType,nodeTags= each[0], each[1], each[2]
                    nodeItemDict={(nodeIdenty+'_'+resType+'_'+str(eachNode)):[] for eachNode in nodeTags}
                    nodeDict={**nodeDict,**nodeItemDict}##Merge two dicts
                elif each[0]=='trussEle':
                    responseType,eleTags =each[1],each[2]
                    eleItemDict={('trussEle_'+responseType+'_'+str(eachEle)):[] for eachEle in eleTags}
                    trussEleResponseDict = {**trussEleResponseDict, **eleItemDict}  ##Merge two dicts
                elif each[0]=='zeroEle':
                    responseType, directions,eleTags = each[1], each[2],each[3]
                    eleItemDict = {('zeroEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    zeroEleResponseDict = {**zeroEleResponseDict, **eleItemDict}  ##Merge two dicts
                    eleDirectDict = {('zeroEle_' + responseType + '_' + str(eachEle)):directions for eachEle in eleTags}
                    zeroEleDirectionDict = {**zeroEleDirectionDict, **eleDirectDict}  ##Merge two dicts
                elif each[0]=='nonEleSection':
                    responseType,sectNum,eleTags=each[1],each[2],each[3]
                    eleItemDict = {('nonEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    nonEleSectResponsesDict = {**nonEleSectResponsesDict, **eleItemDict}  ##Merge two dicts
                    sectNumDict = {('nonEle_' + responseType + '_' + str(eachEle)): sectNum for eachEle in eleTags}
                    nonEleSectNumberDict = {**nonEleSectNumberDict, **sectNumDict}  ##Merge two dicts
                elif each[0]=='nonZeroEle':
                    responseType,eleTags = each[1], each[2]
                    eleItemDict = {('nonZeroEle_' + responseType + '_' + str(eachEle)): [] for eachEle in eleTags}
                    nonZeroEleResponsesDict = {**nonZeroEleResponsesDict, **eleItemDict}  ##Merge two dicts
        ######################################################
        ######################################################
        startTime = time.perf_counter()
        tCurrent = ops.getTime()
        tFinal = currentLength * currentDt
        timeList = [tCurrent]
        maxNumIter=1000
        tol=1.0e-4
        while (tCurrent < tFinal):
            ops.test('NormDispIncr', tol,maxNumIter)
            ops.algorithm('KrylovNewton')
            NewmarkGamma = 0.5
            NewmarkBeta = 0.25
            ops.integrator('Newmark', NewmarkGamma, NewmarkBeta)
            ops.analysis('Transient')
            ok = ops.analyze(1, currentDt)
            if (ok == 0):
                tCurrent = ops.getTime()
                timeList.append(tCurrent)
                endTime = time.perf_counter()
                realTime = endTime - startTime
                ##################################################
                ####################---recorderProcess---###########
                if recordList!=None:
                    if nodeDict:
                        nodeKeys=nodeDict.keys()
                        nodeResNameDict={'disp':'nodeDisp','vel':'nodeVel','accel':'nodeAccel','reaction':'nodeReaction'}
                        if (len(nodeDict[list(nodeKeys)[0]])>=writeInterNum) or (tCurrent>=tFinal):
                            [[resType:=eachkey.split("_")[1],nodeTag:=eachkey.split("_")[2],
                              saveValueList:=nodeDict['node_'+resType+'_'+str(nodeTag)],
                              self.saveInstance.saveNodeTimeHistory(nodeSaveName=eachkey, nodeHistoryList=saveValueList)
                              ] for eachkey in nodeKeys]
                            for eachkey in nodeKeys:
                                nodeDict[eachkey] = []
                        [[resType:=eachkey.split('_')[1],nodeTag:=eachkey.split('_')[2],tempValue1:=[round(tCurrent,4)],
                          tempValue2:=eval(f"ops.{nodeResNameDict[resType]}({nodeTag})"),
                            tempValue3:=[round(tempValue2[i1],6) for i1 in range(3)],
                          tempValue:=tempValue1+tempValue3,
                          nodeDict['node_' + resType + '_' + str(nodeTag)].append(tempValue)] for eachkey in nodeKeys] ##海象运算符加列表解析
                    if trussEleResponseDict:
                        eleKeys = trussEleResponseDict.keys()
                        eleResNameDict = {'axialForce': 'basicForce','axialDeform':'basicDeformation'}
                        if (len(trussEleResponseDict[list(eleKeys)[0]])>=writeInterNum) or (tCurrent>=tFinal):
                            [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],
                              saveValueList:=trussEleResponseDict['trussEle_'+resType+'_'+str(eleTag)],
                              self.saveInstance.saveTrussEleResponseTimeHistory(eleSaveName=eachkey,
                              eleHistoryList=saveValueList)] for eachkey in eleKeys]
                            for eachkey in eleKeys:
                                trussEleResponseDict[eachkey] = []
                        [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],tempValue1:=[round(tCurrent,4)],
                          tempValue2:=[round(eval(f"ops.{eleResNameDict[resType]}({eleTag})[0]"),3)],
                          tempValue:=tempValue1+tempValue2,
                          trussEleResponseDict['trussEle_'+resType+'_'+str(eleTag)].append(tempValue)] for eachkey in eleKeys]
                    if zeroEleResponseDict:
                        eleKeys = zeroEleResponseDict.keys()
                        if (len(zeroEleResponseDict[list(eleKeys)[0]])>=writeInterNum) or (tCurrent>=tFinal):
                            [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],
                              saveValueList:=zeroEleResponseDict['zeroEle_'+resType+'_'+str(eleTag)],
                              self.saveInstance.saveZeroEleResponseTimeHistory(eleSaveName=eachkey,
                              eleHistoryList=saveValueList)] for eachkey in eleKeys]
                            for eachkey in eleKeys:
                                zeroEleResponseDict[eachkey] = []
                        [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],tempValue1:=[round(tCurrent,4)],
                          tempValue2:=eval(f"ops.eleResponse({eleTag},'{resType}')"),
                          tempValue3:=[[round(each,3) for each in tempValue2]],
                          tempValue:= tempValue1 + tempValue3+[zeroEleDirectionDict[eachkey]],
                          zeroEleResponseDict['zeroEle_'+resType+'_'+str(eleTag)].append(tempValue)] for eachkey in eleKeys]##海象操作符
                    if nonEleSectResponsesDict:
                        eleKeys = nonEleSectResponsesDict.keys()
                        digitNumDict = {'sectionForce':3,'sectionDeformation':10}
                        if (len(nonEleSectResponsesDict[list(eleKeys)[0]])>=writeInterNum) or (tCurrent>=tFinal):
                            [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],
                              saveValueList:=nonEleSectResponsesDict['nonEle_'+resType+'_'+str(eleTag)],
                              self.saveInstance.saveNonEleSectResponseTimeHistory(eleSaveName=eachkey,
                            eleHistoryList=saveValueList)] for eachkey in eleKeys]
                            for eachkey in eleKeys:
                                nonEleSectResponsesDict[eachkey] = []
                        [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],
                          tempValue := [round(tCurrent, 4)] + [round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},1)"),
                                                                     digitNumDict[resType]),
                            round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},2)"),digitNumDict[resType]),
                            round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},3)"),digitNumDict[resType]),
                            round(eval(f"ops.{resType}({eleTag},{nonEleSectNumberDict[eachkey]},4)")),digitNumDict[resType]],
                          nonEleSectResponsesDict['nonEle_' + resType + '_' + str(eleTag)].append(tempValue)] for eachkey in eleKeys]
                    if nonZeroEleResponsesDict:
                        eleKeys = nonZeroEleResponsesDict.keys()
                        if (len(nonZeroEleResponsesDict[list(eleKeys)[0]])>=writeInterNum) or (tCurrent>=tFinal):
                            [[resType:=eachkey.split("_")[1],eleTag:=eachkey.split("_")[2],
                              saveValueList:=nonZeroEleResponsesDict[eachkey],
                              self.saveInstance.saveNonZeroEleResponseTimeHistory(eleSaveName=eachkey,
                            eleHistoryList=saveValueList)] for eachkey in eleKeys]
                            for eachkey in eleKeys:
                                nonZeroEleResponsesDict[eachkey] = []
                        [[resType := eachkey.split("_")[1], eleTag := eachkey.split("_")[2],tempValue1:=[round(tCurrent, 4)],
                          tempValue2:=eval(f"ops.eleResponse({eleTag},'{resType}')"),
                        tempValue3:=[round(each,3) for each in tempValue2],tempValue := tempValue1 + tempValue3,
                         nonZeroEleResponsesDict[eachkey].append(tempValue)] for eachkey in eleKeys]
                ###################################
                ###################################
                print('KrylovNewton','ground motion=',self.waveNumber,'tol=',tol,'maxNumIter=',maxNumIter, 'totalTime=',
                      tFinal, 'tCurrent=',"{:.6f}".format(tCurrent),'time cost=', "{:.1f}".format(realTime), 'second')
            else:
                print("The ground motion ",self.waveNumber," failed!")
                break

    def _getNodesDB(self):
        """
        get all nodes coordinates from sqlite database
        Output:[dict]-eg. {node1:[x1,y1,z1],node2:[x2,y2,z2],...}
        """
        nodesReturnList = []
        nodeNames = self.nodeSetNameList
        for nodeName in nodeNames:
            getNodes = self.saveInstance.getNodes(nodeName)
            nodesReturnList += getNodes
        nodesDict = {each['tags']: eval(each['contents']) for each in nodesReturnList}
        return nodesDict

    def _getElementsDB(self):
        """
        get all elements from sqlite database
        Output:[dict]-eg.{ele1:[value1,value2,...],ele2:[value1,value2,...]}
        """
        elesReturnList=[]
        elesNames=self.eleSetNameList
        for eleName in elesNames:
            getEles=self.saveInstance.getEles(eleName)
            elesReturnList+=getEles
        elesDict={each['tags']: eval(each['contents']) for each in elesReturnList}
        return elesDict

    def _getModesDB(self):
        """
        get modal information from sqlite database
        """
        getModes=self.saveInstance.getModes(self.modalNameList[0])
        modesDict = {each['tags']: eval(each['contents']) for each in getModes}
        return modesDict
########################################################################################################################
########################################################################################################################
# if __name__ == '__main__':
    ###############################################




















