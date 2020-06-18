import sys
import serial
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, QTimer, pyqtSlot

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.s
form_class = uic.loadUiType("main.ui")[0]
OK = 'OK'


class SerialThread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.__serial__ = None
        self.__queue__ = []

    @pyqtSlot(str, int, result=str)
    def connect(self, port: str, baud_rate: int):
        try:
            self.__serial__ = serial.Serial(port=port, baudrate=baud_rate)
            return OK
        except serial.SerialException as e:
            return repr(e)

    def run(self):
        while not self.isFinished():
            if self.__serial__ is None:
                continue

            if self.__serial__.readable():
                res = self.__serial__.readline()
                self.__queue__.append(res.decode())

    @pyqtSlot(str, result=str)
    def send(self, data: str):
        if self.__serial__ is None:
            return 'serial is None'
        self.__serial__.write(data)
        return OK

    @pyqtSlot(result=list)
    def flush(self):
        data = self.__queue__
        self.__queue__ = []
        return data


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Serialpy')

        self.Connectbtn.clicked.connect(self.on_click_connect_btn)
        self.Sendbtn.clicked.connect(self.on_click_send_btn)

        self.serial_thread = SerialThread()
        self.serial_thread.start()

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.on_update_serial_mon)
        self.timer.start()

    def on_update_serial_mon(self):
        for data in self.serial_thread.flush():
            self.SerialMon.append(data)

    def throw_if_is_not_ok(self, res: str):
        if res is not OK:
            QMessageBox.warning(self, 'Error', res)
            return False
        return True

    def on_click_connect_btn(self):
        if self.throw_if_is_not_ok(
                self.serial_thread.connect(self.PortCbox.currentText(), int(self.BaudrateCbox.currentText()))
        ):
            self.SerialMon.append('###Serial Connect Success###')
        else:
            self.SerialMon.append('###Serial Connect Failed ###')

    def on_click_send_btn(self):
        op = self.lineEdit.text()
        self.throw_if_is_not_ok(self.serial_thread.send(op.encode()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = WindowClass()
    main.show()
    app.exec_()
