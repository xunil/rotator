from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from serial.tools.list_ports import comports

from math import atan2, pi


class RotatorDisplay(QWidget):
    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 400

    def __init__(self, *args, **kwargs):
        super(RotatorDisplay, self).__init__(*args, **kwargs)

        self.azimuth = 0
        self.target_azimuth = 0
        self.chooser_azimuth = 0
        self.chooser_active = False

        self.setMouseTracking(True)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.show()


    def sizeHint(self):
        return QSize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

    def mouseMoveEvent(self, event):
        xx = event.x() - (self.width() / 2.0)
        yy = event.y() - (self.height() / 2.0)
        theta = atan2(yy, xx)
        d = ((theta * (180 / pi)) + 90) % 360
        self.chooser_active = True
        self.chooser_azimuth = d
        self.update()

    def leaveEvent(self, event):
        self.chooser_active = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Left click!")

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        side = min(self.width(), self.height())
        painter.scale(side / self.DEFAULT_WIDTH, side / self.DEFAULT_HEIGHT)

        degree_pen = QPen(QBrush(QColor(127, 0, 127)), 1.0)
        cardinal_pen = QPen(QBrush(QColor(64, 64, 64)), 3.0)
        pointer_pen = QPen(QBrush(QColor(192, 32, 32)), 5.0)
        chooser_pen = QPen(QBrush(QColor(192, 192, 192)), 3.0)

        chooser_font = QFont('Sans Serif', 14)
        chooser_font_metrics = QFontMetrics(chooser_font)

        azimuth_font = QFont('Sans Serif', 16, QFont.Bold)
        azimuth_font_metrics = QFontMetrics(azimuth_font)

        # Draw compass pips
        painter.save()
        for i in range(0, 360, 15):
            pip_end = 196
            pip_length = 10
            if (i % 90) == 0:
                pip_length = 15
                painter.setPen(cardinal_pen)
            else:
                painter.setPen(degree_pen)
            painter.drawLine(pip_end-pip_length, 0, pip_end, 0)
            painter.rotate(15)
        painter.restore()

        # Paint chooser needle
        if self.chooser_active:
            painter.save()
            painter.setFont(chooser_font)
            painter.setPen(chooser_pen)
            text_x = -(chooser_font_metrics.boundingRect('000').width() / 2)
            # FIXME: Dividing height by 4 puts the text in a bad spot when the window is resized.
            text_y = (self.height() / 4.0) - (chooser_font_metrics.boundingRect('000').height() / 2)
            painter.drawText(text_x, text_y, '{:03d}'.format(round(self.chooser_azimuth)))
            painter.rotate(self.chooser_azimuth-90)
            painter.drawLine(0, 0, 175, 0)
            painter.restore()

        # Paint rotator needle
        painter.save()
        painter.setFont(azimuth_font)
        painter.setPen(pointer_pen)
        text_x = -(azimuth_font_metrics.boundingRect('000').width() / 2)
        # FIXME: Dividing height by 3 puts the text in a bad spot when the window is resized.
        text_y = (self.height() / 3.0) - (azimuth_font_metrics.boundingRect('000').height() / 2)
        painter.drawText(text_x, text_y, '{:03d}'.format(round(self.azimuth)))
        painter.rotate(self.azimuth-90)
        painter.drawLine(0, 0, 175, 0)
        painter.restore()

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('Rotator')
        self.setMouseTracking(True)
        rotator_display = RotatorDisplay(self)
        self.setCentralWidget(rotator_display)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        serial_port_menu = file_menu.addMenu('Serial Port')
        file_menu.addSeparator()
        quit_action = QAction('E&xit', self)
        quit_action.triggered.connect(self.quit_selected)
        file_menu.addAction(quit_action)

        self.serial_ports = {}
        self.serial_ports_action_group = QActionGroup(self)
        self.serial_ports_action_group.setExclusive(True)
        for serial_port in comports():
            if serial_port.device == '':
                continue
            action = QAction(serial_port.description, self.serial_ports_action_group)
            self.serial_ports[serial_port.device] = {'object': serial_port, 'action': action}
            print("serial_port.device={}".format(serial_port.device))
            action.toggled.connect(lambda checked, devname=serial_port.device: self.serial_port_selected(checked, devname))
            action.setCheckable(True)
            serial_port_menu.addAction(action)

        self.show()

    def serial_port_selected(self, checked='Derp', devname='Foo'):
        print('Serial port selected, checked={}, device={}'.format(checked, devname))

    def quit_selected(self):
        print('Exiting')
        QCoreApplication.quit()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()
