# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PyQt5 import QtWidgets, uic
from PyQt5 import QtBluetooth
from PyQt5 import QtCore
from PyQt5.QtBluetooth import QBluetoothLocalDevice

class pyTrainer(QWidget):
    zephyrMAC = "CC:78:AB:5D:FC:B9"

    def __init__(self, parent = None):
        super(pyTrainer, self).__init__(parent)

        self.win = uic.loadUi("mainwindow.ui")
        self.win.show();
        self.win.versionTxtBox.setText("200")

        self.packetTimer = QtCore.QTimer()
        self.packetTimer.timeout.connect(self.packetTimerTick)
        #self.packetTimer.start(1000)

    def packetTimerTick(self):
        self.writeLog("packetTimerTick")
        self.readBTSocket()

    def readBTSocket(self):
        self.packet = self.btSocket.readAll()
        self.writeLog(str(self.packet))

    def test(self):
        print("jfhjkhfk")

    def writeLog(self,text):
        self.win.logPlainTextEdit.appendPlainText(text)

    def zephyrInit(self, btAddress):
        self.btSocket = QtBluetooth.QBluetoothSocket(QtBluetooth.QBluetoothServiceInfo.RfcommProtocol)
        self.btSocket.connected.connect(self.connectedToBluetooth)
        self.btSocket.readyRead.connect(self.receivedBluetoothMessage)
        self.btSocket.disconnected.connect(self.disconnectedFromBluetooth)
        self.btSocket.error.connect(self.socketError)
        self.btSocket.connectToService(QtBluetooth.QBluetoothAddress(btAddress), QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.SerialPort))

        self.localDevice = QtBluetooth.QBluetoothLocalDevice()
        if self.localDevice.isValid():
            self.writeLog("localdevice valid")
            is_off = self.localDevice.hostMode() == QBluetoothLocalDevice.HostPoweredOff or False
            self.writeLog(str(is_off))
            if is_off:
                self.localDevice.setHostMode(QBluetoothLocalDevice.HostDiscoverable)
                self.localDevice.powerOn()
                self.localDevice.setHostMode(QBluetoothLocalDevice.HostDiscoverable)
            else:
                self.localDevice.setHostMode(QBluetoothLocalDevice.HostDiscoverable)
                #self.btSocket.doDeviceDiscovery(QtBluetooth.QBluetoothServiceInfo, QtCore.QIODevice.OpenModeFlag.ReadWrite)
                self.localDevice.requestPairing(QtBluetooth.QBluetoothAddress(btAddress), QtBluetooth.QBluetoothLocalDevice.AuthorizedPaired)
                self.localDevice.pairingFinished.connect(self.devicePairingFinished)
                #self.startServiceDiscovery()


    def devicePairingFinished(self, address, pairing):
        self.writeLog(str(address))
        self.writeLog(str(pairing))
        self.btSocket.connectToService(QtBluetooth.QBluetoothAddress(btAddress), QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.SerialPort))

    def startServiceDiscovery(self):
        # Create a discovery agent and connect to its signals
        self.discoveryAgent = QtBluetooth.QBluetoothServiceDiscoveryAgent()
        self.discoveryAgent.serviceDiscovered.connect(self.discoveryAgent.discoveredServices)
        # Start a discovery
        self.discoveryAgent.start()
        #...

    # In your local slot, read information about the found devices
    def serviceDiscovered(self, service):
        print("Found service():", service.serviceName()) << '(' << service.device().address().toString() << ')'

    def scan_for_devices(self):
        self.agent = QtBluetooth.QBluetoothDeviceDiscoveryAgent(QtBluetooth.QBluetoothAddress(self.zephyrMAC))
        self.agent.deviceDiscovered.connect(self.foo)
        self.agent.finished.connect(self.foo)
        self.agent.error.connect(self.foo)
        self.agent.setLowEnergyDiscoveryTimeout(1000)

    def foo(self, *args, **kwargs):
        print('foo', args, kwargs)

    def hostModeStateChanged(self,state):
        self.writeLog(state)

    def socketError(self,error):
        print(self.btSocket.errorString())
        self.writeLog("socketError")
        self.writeLog(self.btSocket.errorString())

    def connectedToBluetooth(self):
        self.btSocket.write('A'.encode())
        self.writeLog("connectedToBluetooth")

    def disconnectedFromBluetooth(self):
        self.print('Disconnected from bluetooth')
        self.wtiteLog("disconnectedFromBluetooth")

    def receivedBluetoothMessage(self):
        self.wtiteLog("receivedBluetoothMessage")
        while btSocket.canReadLine():
            line = btSocket.readLine()
            writeLog(str(line))

def main():
    if sys.platform == 'darwin':
        os.environ['QT_EVENT_DISPATCHER_CORE_FOUNDATION'] = '1'

    app = QApplication(sys.argv)

    ex = pyTrainer();
    ex.zephyrInit(ex.zephyrMAC)

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

