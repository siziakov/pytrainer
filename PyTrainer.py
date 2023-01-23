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
        self.btSocket.connectToService(QtBluetooth.QBluetoothAddress(self.zephyrMAC), QtBluetooth.QBluetoothUuid(QtBluetooth.QBluetoothUuid.SerialPort))

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
        self.writeLog("connectedToBluetooth")

        startByte = 0x02;
        endByte = 0x03;
        ackByte = 0x06;
        crc = self.crc8PushBlock(None, bytes([ 1 ]));
        self.writeLog("crc = " + str(crc))
        packet = bytes([startByte, 0x14, 0x01, 0x01, crc, endByte])
        #packet = bytes([startByte, 0x14, 0x01, 0x01, 0x5e, endByte])
        self.writeLog("sending packet => " + str(packet))
        res = self.btSocket.write(packet);
        if (res < 0):
            self.writeLog("Error sending packet to device!")
        else:
            self.writeLog("Packet sent.")
        #setZephyrState(waitForGeneralDataModeAccept);

    def crc8PushByte(self, crc, b):
        crc = crc ^ b
        for i in range(0, 8):
            if (crc & 1):
                crc = (crc >> 1) ^ 0x8C
            else:
                crc = crc >> 1
        return crc

    def crc8PushBlock(self, pcrc, block):
        crc = pcrc
        if crc == None:
            crc = 0
        for b in block:
            crc = self.crc8PushByte(crc, b)
        return crc

    def disconnectedFromBluetooth(self):
        self.print('Disconnected from bluetooth')
        self.writeLog("disconnectedFromBluetooth")

    def packetParse(self,packet,startIndex):
        indexOfStartingPacket = packet.indexOf(bytes([0x02, 0x20, 53]), startIndex)
        if (indexOfStartingPacket > -1):
            lastHRReceived = ord(packet.at(indexOfStartingPacket + 12)) + ord(packet.at(indexOfStartingPacket + 13)) * 256
            #in microVolts
            lastECGReceived = min(9999, ord(packet.at(indexOfStartingPacket + 28)) + ord(packet.at(indexOfStartingPacket + 29)) * 256) * 0.000001
            #skin Temperature
            lastSkinTemperature = (ord(packet.at(indexOfStartingPacket + 16)) + ord(packet.at(indexOfStartingPacket + 17)) * 256) * 0.1
            #in microVolts
            lastNoiseReceived = min(9999, ord(packet.at(indexOfStartingPacket + 30)) + ord(packet.at(indexOfStartingPacket + 31)) * 256) * 0.000001
            #in milliVolts
            lastBatteryReceived = (ord(packet.at(indexOfStartingPacket + 24)) + ord(packet.at(indexOfStartingPacket + 25)) * 256) * 0.001
            self.writeLog("HR = " + str(lastHRReceived) + " , T = " + str(lastSkinTemperature) + " , ECG (mcV) = " + str(lastECGReceived) + " , Noise (mcV) = " + str(lastNoiseReceived) + " , Battery (mV) = " + str(lastBatteryReceived))
            self.packetParse(packet, indexOfStartingPacket + 58)

    def receivedBluetoothMessage(self):
        #self.writeLog("receivedBluetoothMessage")
        while self.btSocket.canReadLine():
            packet = self.btSocket.readLine()
            self.packetParse(packet, 0)
            #self.writeLog(str(packet.length()) + "|" + str(packet))
            #if (packet.length() == 5 and packet.at(0) == 0x02 and packet.at(1) == 0x14 and packet.at(2) == 0 and packet.at(4) == 0x06):
            #if (packet.contains(bytes([0x02, 0x14, 0x00, 0x00, 0x06]))):
            #    self.writeLog("activate R to R sendind mode")
            #    crc = self.crc8PushBlock(None, bytes([1]))
            #    new_packet = bytes([0x02, 0x19, 0x01, 0x01, crc, 0x03])
                #res = self.btSocket.write(new_packet)
                #self.writeLog("Error sending packet to device!" if (res < 0) else "Packet sent.")
            #if (packet.length() == 58 and packet.at(0) == 0x02 and packet.at(1) == 0x20 and packet.at(2) == 53 and (packet.at(packet.length() - 1) == 0x03 or packet.at(packet.length() - 1) == 0x06)):
            #indexCommon = packet.indexOf(bytes([0x02, 0x20, 53]))
            #if (indexCommon > -1):
            #    lastHRReceived = ord(packet.at(indexCommon + 12)) + ord(packet.at(indexCommon + 13)) * 256
            #    #in microVolts
            #    lastECGReceived = min(9999, ord(packet.at(indexCommon + 28)) + ord(packet.at(indexCommon + 29)) * 256) * 0.000001
            #    #skin Temperature
            #    lastSkinTemperature = (ord(packet.at(indexCommon + 16)) + ord(packet.at(indexCommon + 17)) * 256) * 0.1
            #    #in microVolts
            #    lastNoiseReceived = min(9999, ord(packet.at(indexCommon + 30)) + ord(packet.at(indexCommon + 31)) * 256) * 0.000001
            #    #in milliVolts
            #    lastBatteryReceived = (ord(packet.at(indexCommon + 24)) + ord(packet.at(indexCommon + 25)) * 256) * 0.001
            #    self.writeLog("HR = " + str(lastHRReceived) + " , T = " + str(lastSkinTemperature) + " , ECG (mcV) = " + str(lastECGReceived) + " , Noise (mcV) = " + str(lastNoiseReceived) + " , Battery (mV) = " + str(lastBatteryReceived))
            #if (packet.length() == 50 and packet.at(0) == 0x02 and packet.at(1) == 0x24 and packet.at(2) == 45 and (packet.at(packet.length() - 1) == 0x03 or packet.at(packet.length() - 1) == 0x06)):
            #indexRR = packet.indexOf(bytes([0x02, 0x24, 45]))
            #if (indexRR > -1):
            #    self.writeLog("RR packet recieved")
            #self.writeLog(str(packet))

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

