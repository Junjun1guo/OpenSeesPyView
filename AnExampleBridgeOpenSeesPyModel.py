#-*-coding: UTF-8-*-
#####Units: Length-m, Force-kN, mass-ton, Stress-kpa(10e-3MPa), g=9.81m/s2
#####Units: Length-mm, Force-N, mass-ton, Stress-Mpa, g=9810mm/s2 pho=ton/mm3
########################################################################################################################
#  Author: Junjun Guo,Tongji University. https://github.com/Junjun1guo
#  E-mail: guojj@tongji.edu.cn/guojj_ce@163.com
#  Environemet: Successfully executed in python 3.8
#  Date: 2022-05-21
########################################################################################################################
########################---import modules---#################################
import numpy as np
import openseespy.opensees as ops
from OpenSeesPyClass import OpenSeesPyClass
from ModalAnalysis import ModalAnalysis
########################################################################################################################
########################################################################################################################
##########---ModelCosntructionAndAnalysis---#######################
#######parameter Setting
caseNumber = 1
waveNumber = 1
############################################################
##################---初始化模型类OpenSeesPyClass---############
ops.wipe()
openseespyInstance = OpenSeesPyClass(caseNumber=caseNumber, waveNumber=waveNumber)  ###初始化OpenSeesPyClass类
sqliteSaveInstance = openseespyInstance.saveInstance  ####得到实例化的数据库
############################################################
##################---定义模型维数及自由度数---##################
openseespyInstance.model_ndm()
############################################################
##################---建立拉索节点---##########################
cableNodes = np.loadtxt('modelInformation/cableNodes.txt')
openseespyInstance.node_create(cableNodes, tipsString='cableNodes')
############################################################
##################---建立拉索材料---##########################
cableMaterial = np.loadtxt('modelInformation/newCableMat.txt')
openseespyInstance.cable_material(cableMaterial, cableYieldStress=1.67e6, tipsString='cableMaterial')
############################################################
##################---建立拉索单元---##########################
cableEle = np.loadtxt('modelInformation/newCableEle.txt')
openseespyInstance.ele_truss(cableEle, tipsString='cableEle')
############################################################
##################---建立主梁节点---##########################
girderNode = np.loadtxt('modelInformation/GirderNode.txt')
openseespyInstance.node_create(girderNode, tipsString='girderNodes')
############################################################
##################---建立主梁局部坐标转换---####################
girderTransf = np.loadtxt('modelInformation/newGirderTransf.txt')
openseespyInstance.geomTransf_PDelta(girderTransf, tipsString='girderTransf')
############################################################
##################---建立主梁单元---##########################
girderEle = np.loadtxt('modelInformation/GirderEle.txt')
openseespyInstance.ele_elasticBeamColum(girderEle, tipsString='girderEle')
###########################################################
##################---建立墩柱节点---#########################
pierNode = np.loadtxt('modelInformation/newPierNodes.txt')
openseespyInstance.node_create(pierNode, tipsString='pierNodes')
###########################################################
##################---建立墩柱局部坐标转换---###################
pierTransf = np.loadtxt('modelInformation/newPierTransfRotate-1.txt')
openseespyInstance.geomTransf_PDelta(pierTransf, tipsString='pierTransf')
###########################################################
##################---建立弹性墩柱单元---######################
elasticPylonEle = np.loadtxt('modelInformation/elasticPylonEle.txt')
openseespyInstance.ele_elasticBeamColum(elasticPylonEle, tipsString='elasticPylonEle')
###########################################################
##################---建立各种单轴材料---######################
"""Construct the various materials"""
print('material constructing start...')
HRB235Number = openseespyInstance.materialReNumber('HRB235')
ops.uniaxialMaterial('Steel01',HRB235Number, 235.e3, 2.1e8, 0.005)
HRB335Number = openseespyInstance.materialReNumber('HRB335')
ops.uniaxialMaterial('Steel01', HRB335Number,335.e3, 2.1e8, 0.005)
HRB400Number = openseespyInstance.materialReNumber('HRB400')
ops.uniaxialMaterial('Steel01',HRB400Number,400.0e3,2.05e8,0.006775)
C40_CoverNumber = openseespyInstance.materialReNumber('C40_Cover')
ops.uniaxialMaterial('Concrete01',C40_CoverNumber,-22780,-0.0020,-22780 * 0.2,-0.004)
C50_CoverNumber = openseespyInstance.materialReNumber('C50_Cover')
ops.uniaxialMaterial('Concrete01',C50_CoverNumber,-27540,-0.0020,-27540 * 0.2,-0.004)
C55_CoverNumber = openseespyInstance.materialReNumber('C55_Cover')
ops.uniaxialMaterial('Concrete01',C55_CoverNumber,-30175,-0.0020,-30175 * 0.2,-0.004)
C40_CoreNumber = openseespyInstance.materialReNumber('C40_Core')
ops.uniaxialMaterial('Concrete01',C40_CoreNumber,-30944,-0.00558,-30944 * 0.2,-0.0282)
C50_CoreNumber = openseespyInstance.materialReNumber('C50_Core')
ops.uniaxialMaterial('Concrete01',C50_CoreNumber,-36759,-0.00535,-36759 * 0.2,-0.0268)
C55_CoreNumber = openseespyInstance.materialReNumber('C55_Core')
ops.uniaxialMaterial('Concrete01',C55_CoreNumber,-42677,-0.00614,-42677 * 0.2,-0.0315)
print('material constructing finish...')
############################################################
##################---建立纤维截面---##########################
###construct upper section
pylonUpperCover = np.loadtxt('fiberInfo/pylonUpper/coverDivide.txt')
pylonUpperCore = np.loadtxt('fiberInfo/pylonUpper/coreDivide.txt')
pylonUpperBar = np.loadtxt('fiberInfo/pylonUpper/barDivide.txt')
pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                     openseespyInstance.materialNumberDict['HRB400']]
openseespyInstance.fiber_section(41082, pylonUpperList, pylonUpperMatList, tipsString="fiberSection")

pylonUpperCover = np.loadtxt('fiberInfo/pierFiber1/coverDivide.txt')
pylonUpperCore = np.loadtxt('fiberInfo/pierFiber1/coreDivide.txt')
pylonUpperBar = np.loadtxt('fiberInfo/pierFiber1/barDivide.txt')
pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
pylonUpperMatList = [openseespyInstance.materialNumberDict['C40_Cover'], openseespyInstance.materialNumberDict['C40_Core'],
                     openseespyInstance.materialNumberDict['HRB400']]
openseespyInstance.fiber_section(11001, pylonUpperList, pylonUpperMatList, tipsString="fiberSection")
for i1 in range(41001, 41019):
    pylonUpperCover = np.loadtxt('fiberInfo/4pylonBottom/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/4pylonBottom/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/4pylonBottom/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
for i1 in range(51001, 51015):
    pylonUpperCover = np.loadtxt('fiberInfo/5pylonBottom/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/5pylonBottom/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/5pylonBottom/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
for i1 in range(41019, 41029):
    pylonUpperCover = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
for i1 in range(41072, 41082):
    pylonUpperCover = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/4pylonMiddle/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
for i1 in range(51015, 51025):
    pylonUpperCover = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
for i1 in range(51068, 51078):
    pylonUpperCover = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_coverDivide.txt')
    pylonUpperCore = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_coreDivide.txt')
    pylonUpperBar = np.loadtxt('fiberInfo/5pylonMiddle/' + str(i1) + '_barDivide.txt')
    pylonUpperList = [pylonUpperCover, pylonUpperCore, pylonUpperBar]
    pylonUpperMatList = [openseespyInstance.materialNumberDict['C55_Cover'], openseespyInstance.materialNumberDict['C55_Core'],
                         openseespyInstance.materialNumberDict['HRB400']]
    openseespyInstance.fiber_section(int(i1), pylonUpperList, pylonUpperMatList, tipsString='fiberSection')
############################################################
##################---建立非线性单元---#########################
nonLinearPylonEle = np.loadtxt('modelInformation/nonLinerPylonEle.txt')
openseespyInstance.ele_nonlinearBeamColumn(nonLinearPylonEle, tipsString='nonLinearEle')
############################################################
##################---建立横梁单元局部坐标转换---#################
crossBeamTransf = np.loadtxt('modelInformation/newCrossBeamTransf.txt')
openseespyInstance.geomTransf_PDelta(crossBeamTransf, tipsString='crossBeamTransf')
############################################################
##################---建立横梁单元---##########################
crossBeamEle = np.loadtxt('modelInformation/crossBeamEle.txt')
openseespyInstance.ele_elasticBeamColum(crossBeamEle, tipsString='crossBeamEle')
############################################################
##################---建立其他节点---###########################
otherNodes = np.loadtxt('modelInformation/newOtherNodes.txt')
openseespyInstance.node_create(otherNodes, tipsString='otherNodes')
#############################################################
##################---建立节点固接---############################
fixList = [19000, 29000, 39000, 49000, 59000, 69000, 79000, 89000, 99000]
openseespyInstance.fix_complete(fixList, tipsString='fix')
#############################################################
##################---建立大刚度单元模拟固接---###################
equlDOF = np.loadtxt('modelInformation/equalDOF.txt')
openseespyInstance.ele_elasticBeamColum(equlDOF, tipsString='equlDOF')
############################################################
##################---建立支座单元---##########################
print('bearing constructing start...')
uniaxialMatExpre=[('ENT', 9000, 1.0E7),('Elastic', 8000, 1.0E8),('ElasticPP', 9001, 2.5E5, 0.002),
                  ('ElasticPP', 9002, 4.5E5, 0.002),('ElasticPP', 9003, 5.0E5, 0.002),('ElasticPP', 9004, 2.5E5, 0.002),
                  ('ElasticPP', 9005, 2.5E5, 0.002),('ElasticPP', 9006, 5.0E5, 0.002),('ElasticPP', 9007, 4.5E5, 0.002),
                  ('ElasticPP', 9008, 4.5E5, 0.002),('ElasticPP', 9009, 2.5E5, 0.002)]
[eval(f"ops.uniaxialMaterial{each}") for each in uniaxialMatExpre]
###############################
specialEleTransfList = []
brTraf = np.loadtxt('modelInformation/newBearingTransf.txt')
bearingEleNode=[(2301, 2301, 2302),(2401, 2401, 2402),(2101, 2101, 2102),(2201, 2201, 2202),(3101, 3101, 3102),
                (3201, 3201, 3202),(4101, 4101, 4102),(4201, 4201, 4202),(5101, 5101, 5102),(5201, 5201, 5202),
                (6101, 6101, 6102),(6201, 6201, 6202),(7101, 7101, 7102),(7201, 7201, 7202),(8101, 8101, 8102),
                (8201, 8201, 8202),(9101, 9101, 9102),(9201, 9201, 9202)]
materialTag=[(9000, 9001, 8000),(9000, 9001, 8000),(9000, 9002, 9002),(9000, 9002, 9002),(9000, 9003, 9003),
             (9000, 9003, 9003),(9000, 9004, 8000),(9000, 9004, 8000),(9000, 9005, 8000),(9000, 9005, 8000),
             (9000, 9006, 9006),(9000, 9006, 9006),(9000, 9007, 9007),(9000, 9007, 9007),(9000, 9008, 9008),
             (9000, 9008, 9008),(9000, 9009, 8000),(9000, 9009, 8000)]
beIn=[0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]
for i1 in range(18):
    ops.element('zeroLength', bearingEleNode[i1][0],bearingEleNode[i1][1],bearingEleNode[i1][2], '-mat',
                materialTag[i1][0],materialTag[i1][1],materialTag[i1][2], '-dir', 1, 2, 3, '-orient', 0, 0, 1,
                            brTraf[beIn[i1]][0], brTraf[beIn[i1]][1], brTraf[beIn[i1]][2])
    specialEleTransfList.append(['specialEle', int(bearingEleNode[i1][1]), int(bearingEleNode[i1][2]),
                                 (0,0,1),(brTraf[beIn[i1]][0],brTraf[beIn[i1]][1],brTraf[beIn[i1]][2])])
sqliteSaveInstance.saveEleLocalCoordSys(SaveName="bearingLocalSys_eleLocCordSys",EleLocalCoordSys=specialEleTransfList)
###########################################################
##################---建立弹簧单元---#########################
print('zerolengthSprings constructing start...')
springStiffnessName = [["U1_1", "U2_1", "U3_1", "R1_1", "R2_1", "R3_1"],
                       ["U1_2", "U2_2", "U3_2", "R1_2", "R2_2", "R3_2"],
                       ["U1_3", "U2_3", "U3_3", "R1_3", "R2_3", "R3_3"],
                       ["U1_4", "U2_4", "U3_4", "R1_4", "R2_4", "R3_4"],
                       ["U1_5", "U2_5", "U3_5", "R1_5", "R2_5", "R3_5"],
                       ["U1_6", "U2_6", "U3_6", "R1_6", "R2_6", "R3_6"],
                       ["U1_7", "U2_7", "U3_7", "R1_7", "R2_7", "R3_7"],
                       ["U1_8", "U2_8", "U3_8", "R1_8", "R2_8", "R3_8"],
                       ["U1_9", "U2_9", "U3_9", "R1_9", "R2_9", "R3_9"]]
stiffVal=[[4.92e6,4.73e6,1.01e7,1.42e9,2.82e8,6.91e8],
          [6.14e6,5.90e6,9.84e6,1.40e9,2.92e8,8.56e8],
          [1.3e7,1.27e7,2.12e7,3.14e9,1.13e9,2.06e9],
          [6.29e7,5.93e7,7.48e7,2.08e10,1.05e10,2.35e10],
          [4.72e7,4.45e7,8.7e7,2.38e10,1.18e10,1.77e10],
          [4.15e6,4.18e6,1.54e7,2.06e9,3.05e8,5.83e8],
          [4.43e6,4.46e6,1.54e7,2.06e9,3.06e8,6.20e8],
          [4.32e6,4.35e6,1.54e7,2.07e9,3.1e8,6.06e8],
          [4.6e6,4.63e6,1.54e7,2.07e9,3.15e8,6.43e8]]

brTraf = np.loadtxt('modelInformation/newBearingTransf.txt')
springEleNode=[(19000, 19000, 19001),(29000, 29000, 29001),(39000, 39000, 39001),(49000, 49000, 49001),
               (59000, 59000, 59001),(69000, 69000, 69001),(79000, 79000, 79001),(89000, 89000, 89001),
               (99000, 99000, 99001)]
specialEleTransfList = []
for i1 in range(9):
    numbers0 = openseespyInstance.materialReNumber(springStiffnessName[i1][0])
    ops.uniaxialMaterial('Elastic', numbers0, stiffVal[i1][0])
    numbers1 = openseespyInstance.materialReNumber(springStiffnessName[i1][1])
    ops.uniaxialMaterial('Elastic', numbers1, stiffVal[i1][1])
    numbers2 = openseespyInstance.materialReNumber(springStiffnessName[i1][2])
    ops.uniaxialMaterial('Elastic', numbers2, stiffVal[i1][2])
    numbers3 = openseespyInstance.materialReNumber(springStiffnessName[i1][3])
    ops.uniaxialMaterial('Elastic', numbers3, stiffVal[i1][3])
    numbers4 = openseespyInstance.materialReNumber(springStiffnessName[i1][4])
    ops.uniaxialMaterial('Elastic', numbers4, stiffVal[i1][4])
    numbers5 = openseespyInstance.materialReNumber(springStiffnessName[i1][5])
    ops.uniaxialMaterial('Elastic', numbers5, stiffVal[i1][5])
    ops.element('zeroLength', springEleNode[i1][0],springEleNode[i1][1],springEleNode[i1][2], '-mat',
                numbers0,numbers1,numbers2,numbers3,numbers4,numbers5, '-dir', 1, 2,3, 4,5, 6,'-orient', 0, 0, 1,
                brTraf[i1][0], brTraf[i1][1], brTraf[i1][2])
    specialEleTransfList.append(['specialEle', int(springEleNode[i1][1]), int(springEleNode[i1][2]),
                                 (0,0,1),(brTraf[i1][0], brTraf[i1][1], brTraf[i1][2])])
    sqliteSaveInstance.saveEleLocalCoordSys(SaveName="nodeSprings_eleLocCordSys",EleLocalCoordSys=specialEleTransfList)
print('zerolengthSprings constructing finish...')
########################################################
##################---施加重力荷载---######################
nodesTags=ops.getNodeTags()
nodesMass=[ops.nodeMass(each)[0] for each in nodesTags]
nodeList=[[node,mass] for node,mass in zip(nodesTags, nodesMass)]
openseespyInstance.gravity_load(nodeList, tipsString='applyGravityLoad')
#########################################################
##################---记录响应---##########################
girderNodeList = [each for each in range(1, 446)]
# openseespyInstance.recorder_node(savePath='responses/GirderNodeDisp', nodeLists=girderNodeList, dofLists=[1, 2, 3,4,5,6],
#                                  responseType='disp', tipsString='girderNodeDisp')
nodeRespList = [41129, 51125, 223]
# openseespyInstance.recorder_node(savePath='responses/nodeDispResponse', nodeLists=nodeRespList, dofLists=[1, 2, 3,4,5,6],
#                                  responseType='disp', tipsString='nodeDispResponse')
# openseespyInstance.recorder_node(savePath='responses/nodeAccResponse', nodeLists=nodeRespList, dofLists=[1, 2, 3,4,5,6],
#                                  responseType='accel', tipsString='nodeAccResponse')
pylonEleNumList = [41001, 41018, 41019, 41081, 41082, 51001, 51014, 51015, 51077, 51078, 11001, 11016, 21001, 21020,
                   31001, 31016, 61001, 61016, 71001, 71020, 81001, 81020, 91001, 91020]
# openseespyInstance.recorder_element(savePath='responses/pylonEleMoment', eleList=pylonEleNumList, responseTypeList=
# ['section', '1', 'force'], tipsString='pylonEleMoment')
# openseespyInstance.recorder_element(savePath='responses/pylonEleDeformation', eleList=pylonEleNumList, responseTypeList=
# ['section', '1', 'deformation'], tipsString='pylonEleDeformation')
cableEleList = [each for each in range(45001, 45039)] + [each for each in range(46001, 46039)]
# openseespyInstance.recorder_element(savePath='responses/cableForce', eleList=cableEleList, responseTypeList=
# ['axialForce'], tipsString='cableForce')
BearingList = [2301, 2101, 3101, 4101, 5101, 6101, 7101, 8101, 9101]
# openseespyInstance.recorder_element(savePath='responses/bearingForce', eleList=BearingList, responseTypeList=
# ['localForce'], tipsString='bearingForce')
# openseespyInstance.recorder_element(savePath='responses/bearingDisp', eleList=BearingList, responseTypeList=
# ['deformation'], tipsString='bearingDisp')
#############################################################
##################---重力分析---###############################
recordList = [('node', 'disp', girderNodeList), ('node', 'disp', nodeRespList), ('node', 'accel', nodeRespList),
              ('trussEle', 'axialForce', cableEleList), ('zeroEle', 'deformation', [1, 2, 3], BearingList),
              ('zeroEle', 'localForce', [1, 2, 3], BearingList),
              ('nonEleSection', 'sectionForce', 1, pylonEleNumList),
              ('nonEleSection', 'sectionDeformation', 1, pylonEleNumList),
              ('nonZeroEle', 'localForce', [41001, 41018, 41019])]
openseespyInstance.analysis_gravity(tipsString='gravityAnalysis',recordList=None)  #if recordList!=None, static anaysis results
###will be writen to the database
##############################################################
##################---模态分析---################################
openseespyInstance.analysis_modal(numModes=100, tipsString='modalAnalysis')
###############################################################
##################---模态分析及整型质量参与系数等---################
# T, Mratios, Mfactors, Mtots = ModalAnalysis(numEigen=300, outname='OpenSeesModalParticipatMass', pflag=1)
###############################################################
##################---时程分析---#################################
#dampingRatio = 0.03
#Longitudinal damping coefficients T1=13.385s T107=0.206s
#Transverse damping coefficients T2=5.057s T131=0.155s
waveLength = np.loadtxt('length.txt')
dtList = np.loadtxt('dt.txt')
acc_X = 'inputGroundMotion/horizontal/' + str(openseespyInstance.waveNumber) + '.txt'
acc_Z = 'inputGroundMotion/vertical/' + str(openseespyInstance.waveNumber) + '.txt'
#######响应记录列表
###########for node, ('node', 'disp', [1, 2, 3])-(keyWord,responseType,nodeTagsList)
###########('node', 'disp', [1, 2, 3]), ('node', 'vel', [1, 2, 3]),('node','accel',[1,2,3]),
###########('node','reaction',[1,2,3])
###########对于truss单元-('trussEle','axialForce',[45001,45002,45003])-（keyword,responseType,eleTags)
###########('trussEle','axialDeform',[45001,45002,45003])
###########对于zeroLength单元，('zeroEle','deformation',[1,2,3],[2301,2101,3101])
##############################('zeroEle','localForce',[1,2,3],[2301,2101,3101])
###########对于nonLinearEle单元section，('nonEleSection','sectionForce',1,[41001, 41018, 41019])
###################('nonEleSection','sectionDeformation',1,[41001, 41018, 41019])
###########对于NonZero单元，('nonZeroEle','localForce',[41001, 41018, 41019])
#############
recordList = [('node', 'disp', girderNodeList),('node', 'disp', nodeRespList),('node', 'accel', nodeRespList),
              ('node', 'vel', nodeRespList),('trussEle','axialForce',cableEleList),('trussEle','axialDeform',cableEleList),
              ('zeroEle','deformation',[1,2,3],BearingList),('zeroEle','localForce',[1,2,3],BearingList),
              ('nonEleSection','sectionForce',1,pylonEleNumList),('nonEleSection','sectionDeformation',1,pylonEleNumList),
              ('nonZeroEle','localForce',[41001, 41025])]
##########if recordList!=None, time history results will be writen to the database
openseespyInstance.earthquake_excite(dampRatio=0.03, Tstart=13.385, Tend=0.206, waveLenthList=waveLength,
                                     dtList=dtList, dirList=[1, 3], motionList=[acc_X, acc_Z],recordList=recordList)
###############################################







