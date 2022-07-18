import configparser
import os
import os.path
import re
import shutil
import sys
import xml.etree.cElementTree as xml
from os.path import abspath
from winreg import *

import PyQt5
import fdb
import pandas as pd
import win32com.client as win32
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog

import design

# Текущая Директория программы TMR-Tracker и Install.log
key = OpenKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\DigiStar\TMR Tracker')
tmr_dir = (QueryValueEx(key, "ApplicationPath")[0])
tmr_dir = os.path.dirname(tmr_dir)
tmr_install_log = tmr_dir+"\\Install.log"


# Текущая директория программы
dir = os.path.abspath(os.curdir)


# Читаем конфиг
ini = configparser.ConfigParser()  # создаём объекта парсера
ini.read(dir + "\\settings.ini")  # читаем конфиг


# Параметры подключения к БД
dbport = 3356
dbhost = '127.0.0.1'

# Ищем путь к папке с настройками
regexp = r"\S:\\\S+\\\S+\\\S+ \S+{\S+}\\"
tmr_settings_xml=''
with open(tmr_install_log, 'rb') as logfile:
    for line in logfile:
        matches = re.search (str(regexp), str(line))
        if matches:
            tmr_settings_xml = matches.group()+"\\Settings.xml"
#print (tmr_settings_xml)


# Находим все базы в settings.xml и заполняем dbs
dbs=[]
tree = xml.parse(tmr_settings_xml)
root = tree.getroot()
for databasepath in root.iter('databasepath'):
    dbs.append(databasepath.text)
print ("Базы на этом компьютере:")
for items in dbs:
    print(items)

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):

        # -------- Инициализация ----------
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__(parent)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # ------- Обработка кнопок -------
        self.b_bd_select.clicked.connect(self.getBD)  # Кнопка выбрать базу
        self.b_find.clicked.connect(self.zzz)  # Кнопка найти базу
        self.b_out_select.clicked.connect(self.getOUT)  # Кнопка путь выгрузки
        self.b_run.clicked.connect(self.export)  # Кнопка экспорт
        self.b_exit.clicked.connect(self.exitNOW)  # Кнопка выход
        self.b_save.clicked.connect(self.saveINI)  # Кнопка сохранить настройки

        # ------------- Поля-- -----------
        self.l_base.setText(ini["main"]["base"])
        self.l_out.setText(ini["main"]["out_path"])
        self.l_bd_num.setText(ini["main"]["farm_num"])

        # ------------- Дата  -----------
        self.d_date.setDate(QtCore.QDate.currentDate())  # Заполняем текущую дату
        self.d_date.setDisplayFormat("yyyy-MM-dd")

        # ----------- Чекбоксы  ---------
        if ini["main"]["dash"] == "True":
            self.c_dash.setChecked(True)
        else:
            self.c_dash.setChecked(False)
        if ini["main"]["xls"] == "True":
            self.c_xls.setChecked(True)
        else:
            self.c_xls.setChecked(False)
        if ini["main"]["xlsx"] == "True":
            self.c_xlsx.setChecked(True)
        else:
            self.c_xlsx.setChecked(False)

    def export(self):
        date = str(self.d_date.text())  # ДАТА
        base = str(self.l_base.displayText())  # Путь к БД
        out = str(self.l_out.displayText())  # Путь для эспорта
        num = str(self.l_bd_num.displayText())  # Номер фермы
        dash = self.c_dash.isChecked()  # Убрать (-)
        xls = self.c_xls.isChecked()  # Экспортв XLS
        xlsx = self.c_xlsx.isChecked()  # Эскпорт в XLSX
        print("Экспорт")
        exportDB(str(date), str(base), str(out), str(num), bool(dash), bool(xls), bool(xlsx))
        msgBox("Экспорт", "Файл успешно сохранен", 1)

    def saveINI(self):
        print("Save")
        ini["main"]["base"] = str(self.l_base.displayText())
        ini["main"]["out_path"] = str(self.l_out.displayText())
        ini["main"]["farm_num"] = str(self.l_bd_num.displayText())
        ini["main"]["dash"] = str(self.c_dash.isChecked())
        ini["main"]["xlsx"] = str(self.c_xlsx.isChecked())
        ini["main"]["xls"] = str(self.c_xls.isChecked())
        try:
            with open(dir + "\\settings.ini", 'w') as configfile:
                ini.write(configfile)
            msgBox("Настройки", "Настройки сохранены.", 1)
        except:
            msgBox("Настройки", "Ошибка сохранения настроек.", 2)

    def exitNOW(self):
        print("Exit")
        exit(0)

    def getBD(self):
        filename, filetype = QFileDialog.getOpenFileName(self,
                                                         "Выбрать файл", ".",
                                                         "FDB File(*.fdb);;All Files(*)")
        print(filename)
        self.l_base.setText(filename)

    def getOUT(self):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        self.l_out.setText(dirlist + "/")

    def zzz(self):
        dialog = design.SecondWindow(self)
        dialog.show()
        """self.secondWin = design.SecondWindow(dbs, self)  # здесь можешь передавать аргументы во второе окно (nameofargument, self)
        self.secondWin.show()"""

        # self.l_out.settext="dcsdc"
        pass  # TODO: Руализовать поиск активной базы


def msgBox(Title, Text, Icon):
    msg = PyQt5.QtWidgets.QMessageBox()
    msg.setWindowTitle(Title)
    msg.setText(Text)
    msg.setIcon(Icon)
    return msg.exec_()


def rusBase(rus_base):
    if re.search(r'[а-яА-ЯёЁ]', rus_base):
        # Удаляем старую базу
        if os.path.exists(dir + "\\tmp.fdb"):
            os.remove(dir + "\\tmp.fdb")
        msgBox("Информация", rus_base + "\n" + "В пути файла присутсвуют русские символы, - копируем локальную базу.",
               1)
        try:
            shutil.copyfile(rus_base, dir + "\\tmp.fdb")
            rus_base = dir + "\\tmp.fdb"
        except:
            msgBox("Информация", "Не удалось скопировать локальную базу.", 1)
    return rus_base


def exportDB(r_date: str, base: str, out: str, num: str, dash: bool, xls: bool, xlsx: bool):
    # Соединение
    base = rusBase(base)
    print("Дата: " + r_date + "\n" +
          "БАЗА: " + base + "\n" +
          "Экспорт: " + out + "\n" +
          "Номер: " + num + "\n" +
          "Убрать (-): " + str(dash) + "\n" +
          "XLS: " + str(xls) + "\n" +
          "XLSX: " + str(xlsx))
    base = rusBase(base)

    try:
        con = fdb.connect(host=dbhost, port=dbport, database=str(base), user='sysdba', password='masterkey',
                          charset='UTF8',
                          fb_library_name=abspath('fbclient.dll'))
        cur = con.cursor()
    except:
        msgBox("Открытие БД", "!!! Ошибка открытия базы данных. Проверьте путь.", 2)

    # Выполняем SQL запрос
    SQL_R1 = """SELECT 
	--Ферма №
	(SELECT	FARMNUMBER FROM	BEDRIJF), 
	--Название фермы
	(SELECT	NAMEFARMER FROM	BEDRIJF),
	--Дата Партии
	CAST(DELIVERED_TIME AS DATE),
	--Имя рациона
	DS_RATION.DISPLAY_NAME,
	--Рацион
	DS_RATION.DESCRIPTION,
	--Группа
	DS_GROUP.DESCRIPTION,
	--Тип группы
	(SELECT	DS_GROUP_TYPE.NAME FROM DS_GROUP_TYPE WHERE DS_GROUP_TYPE.ID = DS_GROUP.GROUP_TYPE), 
	--Поголовье
	DS_BATCH_DELIVERY.HEAD_COUNT HCD,
	--ИнгредиентыID
	DS_INGREDIENT.EXTERNAL_ID,
	--Ингредиент
	DS_INGREDIENT.DESCRIPTION dsID,
	--Требуем. вес/голову
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0),2),
	--Загруженный вес/Голову
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0),2),
	--Требуем.вес
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--Загруженный вес
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--Розданный вес
	round(DS_BATCH_LOAD.LOADED_WEIGHT*(DS_BATCH_DELIVERY.DELIVERED_WEIGHT/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id),2),
	--Треб. сух. вес/голову
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--Загруженный сух. вес/голову
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--Треб. сух. вес
	round(DS_BATCH_LOAD.CALL_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD	WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--Загруженный сух. вес
	round(DS_BATCH_LOAD.LOADED_WEIGHT/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--Розданный сух. вес
	round(DS_BATCH_LOAD.LOADED_WEIGHT*(DS_BATCH_DELIVERY.DELIVERED_WEIGHT/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*DS_BATCH_LOAD.DRYMATTER_PERC / 100,2),
	--Потребление сухого вещества / голову
	round(DS_BATCH_LOAD.LOADED_WEIGHT*((DS_BATCH_DELIVERY.DELIVERED_WEIGHT-DS_BATCH_DELIVERY.WEIGHBACK_AMOUNT)/NULLIF(DS_BATCH_DELIVERY.CALL_WEIGHT,0))/(SELECT NULLIF(sum(DS_BATCH_LOAD.LOADED_WEIGHT),0)/NULLIF(DS_BATCH_delivery.CALL_WEIGHT,0) FROM DS_BATCH_LOAD WHERE DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id)*(DS_BATCH_LOAD.DRYMATTER_PERC / 100)/NULLIF(DS_BATCH_delivery.HEAD_COUNT,0),2),
	--Надои
	(SELECT ROUND(avg(DS_MILK.AMOUNT),0) FROM DS_MILK WHERE DS_MILK.GROUP_ID=DS_BATCH_DELIVERY.GROUP_ID AND CAST(ds_milk.MILK_DATE AS date) = '""" + str(
        r_date) + """') 
FROM DS_BATCH
INNER JOIN DS_RATION ON	DS_RATION.ID = DS_BATCH.RATION_ID
INNER JOIN DS_BATCH_LOAD ON	DS_BATCH_LOAD.BATCH_ID = DS_BATCH.id
INNER JOIN DS_BATCH_DELIVERY ON	DS_BATCH_DELIVERY.BATCH_ID = DS_BATCH.id
INNER JOIN DS_GROUP ON DS_GROUP.ID = DS_BATCH_DELIVERY.GROUP_ID
INNER JOIN DS_INGREDIENT ON	DS_INGREDIENT.ID = DS_BATCH_load.INGREDIENT_ID """ + "WHERE CAST(DELIVERED_TIME AS DATE) = '" + str(
        r_date) + "'"
    # print(SQL_R1)

    SQL_R2 = """SELECT 
	(SELECT FARMNUMBER FROM BEDRIJF), 
	(SELECT NAMEFARMER FROM BEDRIJF), 
	CAST(dbl.LOADED_TIME  AS DATE) cs,
	di.DISPLAY_NAME di, 
	di.DESCRIPTION ds,
	sum(dbl.LOADED_WEIGHT) ss,
	Round(sum(dbl.LOADED_WEIGHT*dbl.DRYMATTER_PERC/100),2) sss
FROM DS_BATCH_LOAD dbl 
INNER JOIN DS_INGREDIENT di ON di.ID = dbl.INGREDIENT_ID
""" + "WHERE CAST(dbl.LOADED_TIME  AS DATE) = '" + str(r_date) + "'" + """
GROUP BY cs, di, ds"""
    # print(SQL_R2)
    try:
        cur.execute(SQL_R1)
        print("Первый запрос обработан")
    except:
        print("Ошибка выполнения первого запроса")

    try:
        df1 = pd.DataFrame(cur.fetchall())
        #df1 = pd.DataFrame(cur.fetchmany(50))

    except:
        print("не понятная хйня в первом отчете")

    df1.rename(
        columns={0: 'Ферма №', 1: 'Название фермы', 2: 'Дата Партии', 3: 'Имя рациона', 4: 'Рацион', 5: 'Группа',
                 6: 'Тип группы', 7: 'Поголовье', 8: 'ИнгредиентыID', 9: 'Ингредиент', 10: 'Требуем. вес/голову',
                 11: 'Загруженный вес/Голову', 12: 'Требуем.вес', 13: 'Загруженный вес', 14: 'Розданный вес',
                 15: 'Треб. сух. вес/голову', 16: 'Загруженный сух. вес/голову', 17: 'Треб. сух. вес',
                 18: 'Загруженный сух. вес', 19: 'Розданный сух. вес', 20: 'Потребление сухого вещества / голову',
                 21: 'Надои'},
        inplace=True)

    try:
        cur.execute(SQL_R2)
        print("Второй запрос обработан")
    except:
        print("Ошибка выполнения второго запроса")

    df2 = pd.DataFrame(cur.fetchall())
    df2.rename(
        columns={0: 'Ферма №', 1: 'Название фермы', 2: 'Дата Партии', 3: 'ИнгредиентыID', 4: 'Ингредиент',
                 5: 'Загруженный вес', 6: 'Загруженный сух. вес'},
        inplace=True)

    # Запись файла
    exls_fname = str(num) + "_" + str(r_date) + '.xlsx'

    if dash == True:
        exls_fname = str(num) + "_" + str.replace(str(r_date), "-", "") + '.xlsx'

    df_sheets = {'Расход ингредиента по группам': df1, 'Общий расход ингредиента': df2}
    writer = pd.ExcelWriter('tmp.xlsx', engine='xlsxwriter')

    for sheet_name in df_sheets.keys():
        df_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    try:
        writer.save()
        writer.close()
    except PermissionError:
        print("!!! Файл таблицы занят")
        sys.exit()

    if xlsx == True:
        shutil.copyfile(dir + "\\tmp.xlsx", out + exls_fname)
        print("Сохраняем в XLSX формате")
        print(f"Файл:{out + exls_fname}")

    if xls == True:
        print("Исправляем файл XLSX-XLS")
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(dir + '\\tmp.xlsx')
        try:
            print("Сохраняем в XLS файл формата Excel 97/2003")
            wb.SaveAs(dir + '\\tmp.xls', 56)
            wb.Close()
            excel.Application.Quit()
            shutil.copyfile(dir + "\\tmp.xls", out + exls_fname[:-1])
            print(f"Файл:{out + exls_fname[:-1]}")
        except:
            print("Нет дуступа к XLS файлу, либо MS Excel не установлен")

    # Очищаем старое
    # cur.close()

    try:
        if os.path.exists(dir + "\\tmp.xls"): os.remove(dir + "\\tmp.xls")
    except:
        print("Не могу удалить tmp.xls")
    try:
        if os.path.exists(dir + "\\tmp.xlsx"): os.remove(dir + "\\tmp.xlsx")
    except:
        print("Не могу удалить tmp.xlsx")


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


# Запуск программы
if __name__ == '__main__':
    main()
