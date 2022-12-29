# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PyQt5 import QtWidgets, uic
from PyQt5 import QtBluetooth

class pyTrainer(QWidget):
    def __init__(self, parent = None):
        super(pyTrainer, self).__init__(parent)
        self.win = uic.loadUi("mainwindow.ui")
        self.win.show();

    def test(self):
        print("jfhjkhfk")

    def zephyrInit(self, btAddress):
        self.btSocket = QtBluetooth.QBluetoothSocket(QtBluetooth.QBluetoothServiceInfo.RfcommProtocol)
        self.btSocket.connected.connect(self.connectedToBluetooth)
        self.btSocket.readyRead.connect(self.receivedBluetoothMessage)
        self.btSocket.disconnected.connect(self.disconnectedFromBluetooth)
        self.btSocket.error.connect(self.socketError)
        self.btSocket.connectToService(QtBluetooth.QBluetoothAddress(btAddress), QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.SerialPort))

    def socketError(self,error):
        print(self.btSocket.errorString())

    def connectedToBluetooth(self):
        self.btSocket.write('A'.encode())

    def disconnectedFromBluetooth(self):
        self.print('Disconnected from bluetooth')

    def receivedBluetoothMessage(self):
        while btSocket.canReadLine():
            line = btSocket.readLine()
            print(line)

def main():
    app = QApplication(sys.argv)
    ex = pyTrainer();
    ex.zephyrInit("98:D3:C1:FD:2C:46")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#app = QtWidgets.QApplication([])
#widget = uic.loadUi("mainwindow.ui")
#widget.show()
#zephyrInit("98:D3:C1:FD:2C:46")
#test()
#sys.exit(app.exec_())

def test():
    print("jfhjkhfk")

