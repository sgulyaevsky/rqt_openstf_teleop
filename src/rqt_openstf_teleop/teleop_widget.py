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
        self._qt_image = None
        self.widget_to_image_scale = 1.0
        self.pressure = 127
        self.horizontal = False

    def paintEvent(self, event):
        """
        Called every tick, paint event of QT
        :param event: Paint event of QT
        """
        if self._cv_image is not None:
            self.update_scale();
            painter = QPainter()
            painter.begin(self)
            painter.fillRect(0,0, self.width(), self.height(), QColor(150, 0, 0))
            painter.drawImage(0, 0, self._qt_image)
            painter.end()

    def set_image(self, image):
        img_height, img_width, _ = image.shape

        if image[img_height//2+16:, :,:].max() == 0:
            image = image[:img_height//2, :,:]
            self.horizontal = True
        else:
            self.horizontal = False

        self._cv_image = image
        self._qt_image = None
        self.update()

    def update_scale(self):
        img_height, img_width, _ = self._cv_image.shape
        kw = 1.0*img_width/self.width()
        kh = 1.0*img_height/self.height()

        k = max(kw, kh)
        self.widget_to_image_scale = k

        w = img_width/k
        h = img_height/k

        if self._qt_image is None or self._qt_image.width() != w or self._qt_image.height() != h:
            scaled_cv_image = cv2.resize(self._cv_image, (int(w), int(h)))
            self._qt_image = _convert_cv_to_qt_image(scaled_cv_image)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.pos().x(), event.pos().y()

            if self.horizontal:
                y, x = event.pos().x(), event.pos().y()
                img_height, img_width, _ = self._cv_image.shape

                x = max(0, img_height/self.widget_to_image_scale - x)

            self.command_signal.emit("d 0 %u %u %u\nc\n" % (
                int(x*self.widget_to_image_scale*2),
                int(y*self.widget_to_image_scale*2), self.pressure))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            x, y = event.pos().x(), event.pos().y()

            if self.horizontal:
                y, x = event.pos().x(), event.pos().y()
                img_height, img_width, _ = self._cv_image.shape
                x = max(0, img_height/self.widget_to_image_scale - x)

            self.command_signal.emit("m 0 %u %u %u\nc\n" % (
                int(x * self.widget_to_image_scale*2),
                int(y * self.widget_to_image_scale*2), self.pressure))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.command_signal.emit("u 0\nc\n")