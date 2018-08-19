from __future__ import absolute_import
from jnius import autoclass

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.config import Config

Config.set(u"graphics", u"resizable", True)
Config.write()

####Bluetooth stuff####
BluetoothAdapter = autoclass(u"android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass(u"android.bluetooth.BluetoothDevice")
BluetoothSocket = autoclass(u"android.bluetooth.BluetoothSocket")
UUID = autoclass(u"java.util.UUID")


class DeviceSelectionScreen(Screen):

    class DeviceButton(Button):

        def __init__(self, outerScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = outerScreen

    def __init__(self, **kwargs):
        super(DeviceSelectionScreen, self).__init__(**kwargs)
        self.rStream = u""
        self.sStream = u""
        deviceNames = self.getDeviceList()
        print deviceNames, u"Device names."


    def setupDevButtons(self, listOfDevs):
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        for devName in listOfDevs:
            btn = self.DeviceButton(self, text=devName, halign=u"left", valign=u"middle")
            self.layout.add_widget(btn)

        self.view.add_widget(self.layout)
        self.add_widget(self.view)

    def getDeviceList(self):
        result = []
        pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for dev in pairedDevs:
            result.append(dev.getName())
        return result


    def createSocketStream(self, devName):
        pairedDevs = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = u""
        for dev in pairedDevs:
            if dev.getName() == devName:
                socket = dev.createRfcommSocketToServiceRecord(UUID.fromString(u"80677070-a2f5-11e8-b568-0800200c9a66")) #Random UUID from https://www.famkruithof.net/uuid/uuidgen
                rStream = socket.getInputStream()   #Recieving data
                sStream = socket.getOutputStream()  #Sending data
                break   #Stop when device found
            socket.connect()
            return rStream, sStream

    def setupBT(self, devName):
        try:
            self.rStream, self.sStream = self.createSocketStream(devName)
        except Exception, e:
            print e, u"Can't connect."
            return u"Select"
        else:
            print u"Connected to:", devName
            return u"Pad"

class PadScreen(Screen, FloatLayout):

    def __init__(self, **kwargs):
        super(PadScreen, self).__init__(**kwargs)
        self.nums = []
        self.numsString = u""

    def addNum(self, num):
        if len(self.nums) < 16:
            self.nums.append(int(num))
            self.numsString += num
            self.updateDisplay()

    def updateDisplay(self):
        self.ids.display.text = self.numsString

    def backSpace(self):
        if len(self.nums) != 0:
            del self.nums[len(self.nums)-1]
            self.numsString = self.numsString[:len(self.nums)]
            #print(self.nums, self.numsString)
            self.updateDisplay()


# class ConfirmationScreen(Screen, FloatLayout):
#
#     def __init__(self, **kwargs):
#         super(ConfirmationScreen, self).__init__(**kwargs)


class ScreenManagement(ScreenManager):
    # LoginScreen = ObjectProperty(None)
    # MainScreen = ObjectProperty(None)
    # addFileScreen = ObjectProperty(None)
    pass


presentation = Builder.load_file(u"pad.kv")

class uiApp(App):

    def build(self):
        return presentation

def runUI():
    ui = uiApp()
    ui.run()


if __name__ == u"__main__":
    runUI()
