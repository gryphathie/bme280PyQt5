import bme280
import smbus2
from time import sleep
import psycopg2
from psycopg2 import Error
import datetime
import numpy as np

from intplot2 import *
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout
import pyqtgraph as pg
import sys, os

port = 1
address = 0x76
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus,address)

t=[]
h=[]
p=[]

class MainWindow(QtWidgets.QMainWindow, Ui:MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Weather Station")

        QTimer.singleShot(200,self.actual)
        self.grafica.setBackground('w')
        self.grafica_2.setBackground('w')
        self.grafica_3.setBackground('w')

    def plot(self):
        self.grafica.plot(t, pen=pg.mkPen('r', width=3))
        self.grafica_2.plot(h, pen=pg.mkPen('b', width=3))
        self.grafica_3.plot(p, pen=pg.mkPen('g', width=3))
        QTimer.singleShot(200,self.actual)

    def actual(self):
        try:
            connection = psycopg2.connect(user="pi",
                                          password="raspberry",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="DatosSensores")

            if True:
                bme280_data = bme280.sample(bus, address)
                humidity = bme280_data.humidity
                pressure = bme280_data.pressure
                temperature = bme280_data.temperature
                sleep(0.3)

                humidity = float(humidity)
                pressure = float(pressure)
                temperature = float(temperature)
                cursor = connection.cursor()
                t.append(temperature)
                h.append(humidity)
                p.append(pressure)

                insert_table_data1 = "insert into humedad values (%s, %s)"
                arg1 = (datatime.datetime.now().timestamp(), humidity)
                insert_table_data2 = "insert into temperatura values (%s, %s)"
                arg2 = (datatime.datetime.now().timestamp(), temperature)
                insert_table_data3 = "insert into presion values (%s, %s)"
                arg3 = (datatime.datetime.now().timestamp(), pressure)

                cursor.execute(insert_table_data1, arg1)
                cursor.execute(insert_table_data2, arg2)
                cursor.execute(insert_table_data3, arg3)

                self.listat.addItem(str(round(temperature,2)))
                self.listah.addItem(str(round(humidity,2)))
                self.listatp.addItem(str(round(pressure,2)))
                self.lcdNumbert.display(temperature)
                self.lcdNumberth.display(humidity)
                self.lcdNumbertp.display(pressure)
                c = self.listat.count()
                if c >= 11:
                    self.listat.clear()
                    self.listah.clear()
                    self.listatp.clear()

                connection.commit()
                print("Succesfully uploaded data to Postgres")

            except(Exception, psycopg2.DatabaseError) as error:
                print("Error while creating Postgres table")

            finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    print("Postgres connection is closed")
                QTimer.singleShot(200,self.plot)

if __name__== "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()




                
