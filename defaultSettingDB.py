# -*- coding: utf-8 -*-
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
import records
import numpy as np
import random
########################################################################################################################
class DefaultSet(object):
    """GUI default properties database"""
    dbPath = "defaultSettingDB.db"
    def __init__(self):
        self._dbPath="defaultSettingDB.db"

    def initDB(self):
        """Initialize the database"""
        self.db = records.Database('sqlite:///'+self._dbPath)
        tableNames=self.db.get_table_names()
        for each in tableNames:
            self.db.query("DROP TABLE IF EXISTS "+each)

    @classmethod
    def upDateValue(cls,tableName,tagName,tagValue):
        """Property values saving"""
        db = records.Database('sqlite:///'+cls.dbPath)
        sql_create_table = f"""
                        CREATE TABLE IF NOT EXISTS
                        {tableName}(
                        {tagName} MESSAGE_TEXT NOT NULL);"""
        db.query(sql_create_table)
        conn = db.get_connection()
        try:
            rows=conn.query(f"""SELECT *FROM {tableName};""")
            saveValue=rows.all(as_dict=True)[0][tagName]
            conn = db.get_connection()
            updateString=f""" UPDATE {tableName} SET {tagName}='{tagValue}';"""
            conn.query(updateString)
        except:
            insertValue=f"""INSERT INTO {tableName}({tagName}) values (:{tagName})"""
            insertDict={tagName:tagValue}
            db.query(insertValue,**insertDict)

    @classmethod
    def getValue(cls,tableName,tagName):
        """Inquire"""
        db = records.Database('sqlite:///' + cls.dbPath)
        conn = db.get_connection()
        try:
            rows = conn.query(f"""SELECT *FROM {tableName} """)
            saveValue = rows.all(as_dict=True)[0][tagName]
            return saveValue
        except:
            print(tableName + ' or ' + tagName + ' not exist in the dataBase!')
            if tableName=="backGroundColorTable":
                saveValue="#000000"
            else:
                initColorList = ["#aa0000", "#00aa00", "#aaff00", "#00007f", "#0000ff", "#aa00ff", "#00aaff", "#ff0000",
                                 "#ffaa00","#55aa7f", "#ff00ff", "#ffaaff"]
                saveValue=random.choice(initColorList)

                db = records.Database('sqlite:///' + cls.dbPath)
                sql_create_table = f"""
                                        CREATE TABLE IF NOT EXISTS
                                        {tableName}(
                                        {tagName} MESSAGE_TEXT NOT NULL);"""
                db.query(sql_create_table)
                insertValue = f"""INSERT INTO {tableName}({tagName}) values (:{tagName})"""
                insertDict = {tagName: saveValue}
                db.query(insertValue, **insertDict)
            return saveValue
########################################################################################################################
# if __name__ == '__main__':
    # dbInstance=DefaultSet()
    # dbInstance.initDB()
    # DefaultSet.upDateValue(tableName="nodecolorTable",tagName="nodeColor",tagValue="red")
    # value=DefaultSet.getValue(tableName="colorTable", tagName="nodeColor")
    # print(value)







