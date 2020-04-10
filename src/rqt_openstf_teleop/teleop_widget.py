from python_qt_binding.QtWidgets import *
from python_qt_binding.QtGui import *
from python_qt_binding.QtCore import *
import cv2


def _convert_cv_to_qt_image(cv_image):
    """
    Method to convert an opencv image to a QT image
    :param cv_image: The opencv image
    :return: The QT Image
    """
    cv_image = cv_image.copy()  # Create a copy
    height, width, byte_value = cv_image.shape
    byte_value = byte_value * width
    cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB, cv_image)

    return QImage(cv_image, width, height, byte_value, QImage.Format_RGB888)


class TeleopWidget(QWidget):
    command_signal = pyqtSignal('QString')

    def __init__(self):
        super(TeleopWidget, self).__init__()
        self._cv_image = None
        self._qt_image = QImage()
        self.widget_to_image_scale = 1.0
        self.pressure = 127

    def paintEvent(self, event):
        """
        Called every tick, paint event of QT
        :param event: Paint event of QT
        """
        if not self._qt_image.isNull():
            painter = QPainter()
            painter.begin(self)
            painter.fillRect(0,0, self.width(), self.height(), QColor(150, 0, 0))
            painter.drawImage(self.active_rect(), self._qt_image)
            # painter.setRenderHint(QPainter.Antialiasing)
            # painter.setPen(QPen(Qt.cyan, 5.0))
            #
            # painter.setFont(QFont('Decorative', 10))
            # for rect, label in self.detections:
            #     painter.setPen(QPen(Qt.magenta, 5.0))
            #     painter.drawRect(rect)
            #
            #     painter.setPen(QPen(Qt.magenta, 5.0))
            #     painter.drawText(rect, Qt.AlignCenter, label)

            painter.end()

    def set_image(self, image):
        """
        Sets an opencv image to the widget
        :param image: The opencv image
        """
        self._cv_image = image
        self._qt_image = _convert_cv_to_qt_image(image)
        self.update()

    def active_rect(self):
        kw = 1.0*self._qt_image.width()/self.width()
        kh = 1.0*self._qt_image.height()/self.height()

        k = max(kw, kh)
        self.widget_to_image_scale = k

        w = self._qt_image.width()/k
        h = self._qt_image.height()/k

        dest_rect = QRectF(0, 0, w, h)
        return dest_rect


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.command_signal.emit("d 0 %u %u %u" % (
                int(event.pos().x()*self.widget_to_image_scale),
                int(event.pos().y()*self.widget_to_image_scale), self.pressure))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.command_signal.emit("m 0 %u %u %u" % (
                int(event.pos().x() * self.widget_to_image_scale),
                int(event.pos().y() * self.widget_to_image_scale), self.pressure))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.command_signal.emit("u 0")