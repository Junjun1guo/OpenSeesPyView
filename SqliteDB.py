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
########################################################################################################################
########################---import modules---#################################
import records
########################################################################################################################
class SqliteDB(object):
    """Save the data to sqlite database"""
    def __init__(self,dbPath):
        """
        Initialize the class
        Inputs:
            dbPath(str)-the path of the database
        """
        self._dbPath = dbPath

    @classmethod
    def initDB(self,dbPath):
        """Initialize the database"""
        self.db = records.Database('sqlite:///' + dbPath)
        tableNames=self.db.get_table_names()
        for each in tableNames:
            self.db.query("DROP TABLE IF EXISTS " + each)
        import sqlite3
        con = sqlite3.connect(dbPath)
        con.execute("VACUUM")
        con.close()


    def saveNodes(self,nodesSaveName,nodeList):
        """Save nodes to database, [[nodeTag,xCoord,yCoord,zCoord...],[],...]"""
        db = records.Database('sqlite:///' + self._dbPath)
        nodesDict=[{'tags':int(each[0]),'contents':str(each[1:])} for each in nodeList]
        nodesTable = f"""
                        CREATE TABLE IF NOT EXISTS
                        {nodesSaveName}(
                        tags INT NOT NULL,
                        contents MESSAGE_TEXT NOT NULL);"""
        db.query(nodesTable)
        insertNodes = f"""
                        INSERT INTO
                        {nodesSaveName}(tags,contents)
                        values (:tags,:contents) """
        db.bulk_query(insertNodes, nodesDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getNodes(self,saveNodeName):
        """
        return nodes from database
        saveNodeName(str)-the table name of saved nodes
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from {saveNodeName};''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table {saveNodeName} doesn't exitst!''')
            return

    def saveEles(self,elesSaveName,elesList):
        """Save nodes to database, [[eleTag,nodeI,nodeJ,...],[],...]"""
        db = records.Database('sqlite:///' + self._dbPath)
        elesDict=[{'tags':int(each[0]),'contents':str(each[1:])} for each in elesList]
        nodesTable = f"""
                        CREATE TABLE IF NOT EXISTS
                        {elesSaveName}(
                        tags INT NOT NULL,
                        contents MESSAGE_TEXT NOT NULL);"""
        db.query(nodesTable)
        insertNodes = f"""
                        INSERT INTO
                        {elesSaveName}(tags,contents)
                        values (:tags,:contents) """
        db.bulk_query(insertNodes,elesDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getEles(self,saveElesName):
        """
        return elements from database
        saveElesName(str)-the table name of saved eles
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from {saveElesName};''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table {saveNodeName} doesn't exitst!''')
            return

    def saveModes(self,modesName,modesList):
        """Save modes to database, [[nodeTag,[mode1value,mode2value],...],[],...]"""
        db = records.Database('sqlite:///' + self._dbPath)
        nodesDict = [{'tags': int(each[0]), 'contents': str(each[1:])} for each in modesList]
        nodesTable = f"""
                                CREATE TABLE IF NOT EXISTS
                                {modesName}(
                                tags INT NOT NULL,
                                contents MESSAGE_TEXT NOT NULL);"""
        db.query(nodesTable)
        insertNodes = f"""
                                INSERT INTO
                                {modesName}(tags,contents)
                                values (:tags,:contents) """
        db.bulk_query(insertNodes, nodesDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getModes(self,saveModesName):
        """
        return modes from database
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from {saveModesName};''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table {saveModesName} doesn't exitst!''')
            return

    def savePeriod(self,periodList):
        """Save periods to database, [[periodNum,value],[],...]"""
        db = records.Database('sqlite:///' + self._dbPath)
        periodDict = [{'tags': int(each[0]), 'contents': str(each[1:])} for each in periodList]
        periodTable = f"""
                                        CREATE TABLE IF NOT EXISTS
                                        periods(
                                        tags INT NOT NULL,
                                        contents MESSAGE_TEXT NOT NULL);"""
        db.query(periodTable)
        insertPeriods = f"""
                                        INSERT INTO
                                        periods(tags,contents)
                                        values (:tags,:contents) """
        db.bulk_query(insertPeriods, periodDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getPeriod(self):
        """
        return periods from database
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from periods;''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table periods doesn't exitst!''')
            return

    def saveGeomTransf(self,geomTransfSaveName,geomfList):
        """
        Save the geomTransf to Database
        geomTransfSaveName(str)-the name of the saved table
        geomfList(list)-[[geomfTag1,localZX_1,localZY_1,localZZ_1],[geomfTag2,localZX_2,localZY_2,localZZ_2],...]
        """
        db = records.Database('sqlite:///' + self._dbPath)
        geomfDict = [{'tags': int(each[0]), 'contents': str(each[1:])} for each in geomfList]
        geomfTable = f"""
                                CREATE TABLE IF NOT EXISTS
                                {geomTransfSaveName}(
                                tags INT NOT NULL,
                                contents MESSAGE_TEXT NOT NULL);"""
        db.query(geomfTable)
        insertGeomf = f"""
                                INSERT INTO
                                {geomTransfSaveName}(tags,contents)
                                values (:tags,:contents) """
        db.bulk_query(insertGeomf, geomfDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getGeomTransf(self, saveGeomTransfName):
        """
        return geomTransf from database
        saveGeomTransfName(str)-the table name of saved geomTransf
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from {saveGeomTransfName};''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table {saveGeomTransfName} doesn't exitst!''')
            return

    def saveEleLocalCoordSys(self,SaveName,EleLocalCoordSys):
        """
        Save element local coordinate systems to database
        localZSaveName(str)-the name of the saved table
        localZList(list)-for real length element, [['realEle',nodeI,nodeJ,localZTag]]
                        -for zeroLength ele or node, [['specialEle',nodeI,nodeJ,(localX_x,localX_y,localX_z),
                        (localY_x,localY_y,localY_z)]]
        """
        db = records.Database('sqlite:///' + self._dbPath)
        geomfDict = [{'tags': str(each[0]), 'contents': str(each[1:])} for each in EleLocalCoordSys]
        geomfTable = f"""
                                        CREATE TABLE IF NOT EXISTS
                                        {SaveName}(
                                        tags INT NOT NULL,
                                        contents MESSAGE_TEXT NOT NULL);"""
        db.query(geomfTable)
        insertGeomf = f"""
                                        INSERT INTO
                                        {SaveName}(tags,contents)
                                        values (:tags,:contents) """
        db.bulk_query(insertGeomf, geomfDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getEleLocalCoordSys(self, saveEleLocalCoordSysName):
        """
        return EleLocalCoordSys from database
        saveEleLocalCoordSysName(str)-the table name of saved EleLocalCoordSysName
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        try:
            queryValue = conn.query(f'''select * from {saveEleLocalCoordSysName};''')
            returnValue = queryValue.all(as_dict=True)
            return returnValue
        except:
            print(f'''table {saveEleLocalCoordSysName} doesn't exitst!''')
            return

    def saveNodeTimeHistory(self,nodeSaveName,nodeHistoryList):
        """
        ---Save node time history responses to database---
        Inputs:
            nodeSaveName(str)-a table name for the saved responses, e.g,'node_disp_1'
            nodeHistoryList(list)-e.g.,[[time0,U1_0,U2_0,U3_0],[time1,U1_1,U2_1,U3_1],...]
        """
        nodeResponseDict = [{'times': float(each[0]), 'dof_1': float(each[1]),'dof_2': float(each[2]),'dof_3': float(each[3])
                             } for each in nodeHistoryList]
        nodesTable = f"""
                        CREATE TABLE IF NOT EXISTS
                        {nodeSaveName}(
                        times REAL NOT NULL,
                        dof_1 REAL NOT NULL,
                        dof_2 REAL NOT NULL,
                        dof_3 REAL NOT NULL);"""
        self.db.query(nodesTable)  # 创建列表
        insertNodes = f"""
                        INSERT INTO
                        {nodeSaveName}(times,dof_1,dof_2,dof_3)
                        values (:times,:dof_1,:dof_2,:dof_3) """
        self.db.bulk_query(insertNodes,nodeResponseDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()


    def getNodeTimeHistory(self,nodeTag,resType,dof):
        """
        ---return node time history response---
        Inputs:
            nodeTag(int)-the tag of the inquried node
            resType(str)-node response type, resType='disp','vel','accel' or 'reaction'
            dof(int)-return the corresponding dof response,dof=1,2 or 3
        Outputs:
            historyResList(list),[times0,times1,times2,...],[response0,response1,response2,...]
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        tableName='node_'+resType+'_'+str(nodeTag)
        dofDict={1:'dof_1',2:'dof_2',3:'dof_3'}
        try:
            queryValue = conn.query(f'''select times,{dofDict[dof]} from {tableName};''')
            returnValue = queryValue.all(as_dict=True)
        except:
            print(f'''Something is wrong. Please check the parameters!''')
            return
        timesList=[]
        responseList=[]
        [[timesList.append(each['times']),responseList.append(each[dofDict[dof]])] for each in returnValue]
        return timesList,responseList

    def saveTrussEleResponseTimeHistory(self,eleSaveName,eleHistoryList):
        """
        ---Save truss element axial force and deformation database---
        elesSaveName(str)-a table name for saved truss element responses, e.g. 'element_axialForce_1','element_axialDeform_1'
        eleHistoryList(list)-e.g.,[[time0,resValue0],[time1,resValue1],...]
        """
        eleResponseDict = [
            {'times': float(each[0]), 'resValue': float(each[1])} for each in eleHistoryList]
        nodesTable = f"""
                                CREATE TABLE IF NOT EXISTS
                                {eleSaveName}(
                                times REAL NOT NULL,
                                resValue REAL NOT NULL);"""
        self.db.query(nodesTable)  # 创建列表
        insertNodes = f"""
                                INSERT INTO
                                {eleSaveName}(times,resValue)
                                values (:times,:resValue) """
        self.db.bulk_query(insertNodes,eleResponseDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getTrussEleResponseTimeHistory(self,eleTag,resType):
        """
        ---Return the truss element time history response---
        Inputs:
            eleTag(int)-the tag of the inquried element
            resType(str)-element response type, resType='axialForce','axialDeform'
        Outputs:
            timesList,responsesList

        """
        tableName='trussEle_'+resType+'_'+str(eleTag)
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        tableName = 'trussEle_' + resType + '_' + str(eleTag)
        try:
            queryValue = conn.query(f'''select times,resValue from {tableName};''')
            returnValue = queryValue.all(as_dict=True)
        except:
            print(f'''Something is wrong. Please check the parameters!''')
            return
        timesList = []
        responseList = []
        [[timesList.append(each['times']), responseList.append(each['resValue'])] for each in returnValue]
        return timesList, responseList

    def saveZeroEleResponseTimeHistory(self,eleSaveName,eleHistoryList):
        """
        ---Save zeroLength element responses database---
        elesSaveName(str)-a table name for saved truss element responses, e.g. 'zeroEle_deformation_1','zeroEle_localForce_1'
        eleHistoryList(list)-e.g.,[[time0,[resValue0_1,resValue0_2,resValue0_3],[1,2,3]],[],...]
        """
        directions=eleHistoryList[0][2]
        linkstr=f"[{{'times': float(each[0]),"
        for iDir in range(len(directions)-1):
            linkstr+=f"'dof_{directions[iDir]}':float(each[1][{iDir}]),"
        linkstr += f"'dof_{directions[-1]}':float(each[1][-1])}} for each in {eleHistoryList}]"
        eleResponseDict =eval(linkstr)

        linkstrTable=f"""
                        times REAL NOT NULL,
                      """
        for iTable in range(len(directions) - 1):
            linkstrTable += f"""dof_{directions[iTable]} REAL NOT NULL,
                            """
        linkstrTable += f"""dof_{directions[-1]} REAL NOT NULL"""
        nodesTable = f"""
                                        CREATE TABLE IF NOT EXISTS
                                        {eleSaveName}({linkstrTable});"""
        self.db.query(nodesTable)
        repreLinkStr=f"""times,"""
        for iTable in range(len(directions) - 1):
            repreLinkStr+=f"""dof_{directions[iTable]},"""
        repreLinkStr+=f"""dof_{directions[-1]}"""
        realLinkStr=f""":times,"""
        for iTable in range(len(directions) - 1):
            realLinkStr+=f""":dof_{directions[iTable]},"""
        realLinkStr += f""":dof_{directions[-1]}"""
        insertNodes = f"""
                    INSERT INTO
                    {eleSaveName}({repreLinkStr})
                    values ({realLinkStr}) """
        self.db.bulk_query(insertNodes, eleResponseDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getZeroEleResponseTimeHistory(self,eleTag,resType,dof):
        """
        ---Return the zeroLength element time history response---
        Inputs:
            eleTag(int)-the tag of the inquried element
            resType(str)-element response type, resType='localForce','deformation'
            dof(int)-return the corresponding dof response,dof=1,2,or 3
        Outputs:
            timesList,responsesList
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        tableName = 'zeroEle_' + resType + '_' + str(eleTag)
        dofDict = {1: 'dof_1', 2: 'dof_2', 3: 'dof_3', 4: 'dof_4', 5: 'dof_5', 6: 'dof_6'}
        try:
            queryValue = conn.query(f'''select times,{dofDict[dof]} from {tableName};''')
            returnValue = queryValue.all(as_dict=True)
        except:
            print(f'''Something is wrong. Please check the parameters!''')
            return
        timesList = []
        responseList = []
        [[timesList.append(each['times']), responseList.append(each[dofDict[dof]])] for each in returnValue]
        return timesList, responseList

    def saveNonEleSectResponseTimeHistory(self,eleSaveName,eleHistoryList):
        """
        ---Save nonlinear element section responses database---
        elesSaveName(str)-a table name for saved truss element responses, e.g. 'nonEle_sectionForce_1','nonEle_sectionDeformation_1'
        eleHistoryList(list)-e.g.,[[time0,response0_1,response0_2,response0_3,responses0_4],[],...]
        """
        eleResponseDict = [{'times': float(each[0]), 'dof_1': float(each[1]),
            'dof_2': float(each[2]),'dof_3': float(each[3]),'dof_4': float(each[4])} for each in eleHistoryList]
        nodesTable = f"""
                        CREATE TABLE IF NOT EXISTS
                        {eleSaveName}(
                        times REAL NOT NULL,
                        dof_1 REAL NOT NULL,
                        dof_2 REAL NOT NULL,
                        dof_3 REAL NOT NULL,
                        dof_4 REAL NOT NULL);"""
        self.db.query(nodesTable)  # 创建列表
        insertNodes = f"""
                        INSERT INTO
                        {eleSaveName}(times,dof_1,dof_2,dof_3,dof_4)
                        values (:times,:dof_1,:dof_2,:dof_3,:dof_4) """
        self.db.bulk_query(insertNodes, eleResponseDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getNonEleSectResponseTimeHistory(self,eleTag,resType,dof):
        """
        ---Return the nonlinear element section time history response---
        Inputs:
            eleTag(int)-the tag of the inquried element
            resType(str)-element response type, resType='sectionForce','sectionDeformation'
            dof(int)-return the corresponding dof response,dof=1,2,3,or 4
                   1-axial direction, 2-rotate about local z,3-rotate about local y, 4-rotate about local x
        Outputs:
            timesList,responsesList
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        tableName = 'nonEle_' + resType + '_' + str(eleTag)
        dofDict = {1: 'dof_1', 2: 'dof_2', 3: 'dof_3', 4: 'dof_4'}
        try:
            queryValue = conn.query(f'''select times,{dofDict[dof]} from {tableName};''')
            returnValue = queryValue.all(as_dict=True)
        except:
            print(f'''Something is wrong. Please check the parameters!''')
            return
        timesList = []
        responseList = []
        [[timesList.append(each['times']), responseList.append(each[dofDict[dof]])] for each in returnValue]
        return timesList, responseList

    def saveNonZeroEleResponseTimeHistory(self,eleSaveName,eleHistoryList):
        """
        ---Save non zerolength element localForce responses database---
        elesSaveName(str)-a table name for saved truss element responses, e.g. 'nonZeroEle_localForce_1'
        eleHistoryList(list)-e.g.,[[time0,response0_I1,response0_I2,response0_I3,response0_I4,response0_I5,
        response0_I6,response0_J1,response0_J2,response0_J3,response0_J4,response0_J5,response0_J6],[],...]
        """
        eleResponseDict = [{'times': float(each[0]), 'dofI_1': float(each[1]),
            'dofI_2': float(each[2]), 'dofI_3': float(each[3]), 'dofI_4': float(each[4]),'dofI_5': float(each[5]),
            'dofI_6': float(each[6]),'dofJ_1': float(each[7]),'dofJ_2': float(each[8]),'dofJ_3': float(each[9]),
            'dofJ_4': float(each[10]),'dofJ_5': float(each[11]),'dofJ_6': float(each[12])} for each in eleHistoryList]
        nodesTable = f"""
                                CREATE TABLE IF NOT EXISTS
                                {eleSaveName}(
                                times REAL NOT NULL,
                                dofI_1 REAL NOT NULL,
                                dofI_2 REAL NOT NULL,
                                dofI_3 REAL NOT NULL,
                                dofI_4 REAL NOT NULL,
                                dofI_5 REAL NOT NULL,
                                dofI_6 REAL NOT NULL,
                                dofJ_1 REAL NOT NULL,
                                dofJ_2 REAL NOT NULL,
                                dofJ_3 REAL NOT NULL,
                                dofJ_4 REAL NOT NULL,
                                dofJ_5 REAL NOT NULL,
                                dofJ_6 REAL NOT NULL);"""
        self.db.query(nodesTable)  # 创建列表
        insertNodes = f"""
                                INSERT INTO
                                {eleSaveName}(times,dofI_1,dofI_2,dofI_3,dofI_4,dofI_5,dofI_6,dofJ_1,dofJ_2,
                                dofJ_3,dofJ_4,dofJ_5,dofJ_6)
                                values (:times,:dofI_1,:dofI_2,:dofI_3,:dofI_4,:dofI_5,:dofI_6,
                                :dofJ_1,:dofJ_2,:dofJ_3,:dofJ_4,:dofJ_5,:dofJ_6) """
        self.db.bulk_query(insertNodes, eleResponseDict)
        db = records.Database('sqlite:///' + self._dbPath)
        db.close()

    def getNonZeroEleResponseTimeHistory(self,eleTag,resType,eleEnd,dof):
        """
        ---Return the non zerolength element time history response---
        Inputs:
            eleTag(int)-the tag of the inquried element
            resType(str)-element response type, resType='localForce'
            eleEnd(str)-the end of the element, 'I' or 'J'
            dof(int)-return the corresponding dof response,dof=1,2,3,4,5 or 6
        Outputs:
            timesList,responsesList
        """
        db = records.Database('sqlite:///' + self._dbPath)
        conn = db.get_connection()
        tableName = 'nonZeroEle_' + resType + '_' + str(eleTag)
        inqTag=eleEnd+'_'+str(dof)
        dofDict = {'I_1': 'dofI_1','I_2': 'dofI_2','I_3': 'dofI_3','I_4': 'dofI_4','I_5': 'dofI_5','I_6': 'dofI_6',
                   'J_1': 'dofJ_1','J_2': 'dofJ_2','J_3': 'dofJ_3','J_4': 'dofJ_4','J_5': 'dofJ_5','J_6': 'dofJ_6'}
        try:
            queryValue = conn.query(f'''select times,{dofDict[inqTag]} from {tableName};''')
            returnValue = queryValue.all(as_dict=True)
        except:
            print(f'''Something is wrong. Please check the parameters!''')
            return
        timesList = []
        responseList = []
        [[timesList.append(each['times']), responseList.append(each[dofDict[inqTag]])] for each in returnValue]
        return timesList, responseList
########################################################################################################################
########################################################################################################################
if __name__ == '__main__':
    dbPath = "resultsDB_1_114.db"
    dbInstance=SqliteDB(dbPath)
    timesList,resList=dbInstance.getNodeTimeHistory(1,'disp',1)
    print(timesList,resList)

