import os
import rospy
import rospkg

from std_msgs.msg import String

from qt_gui.plugin import Plugin


from teleop_widget import TeleopWidget

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class TeleopPlugin(Plugin):
    def __init__(self, context):
        super(TeleopPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print 'arguments: ', args
            print 'unknowns: ', unknowns

        # Create Widget
        self._widget = TeleopWidget()
        self._widget.command_signal.connect(self._command_callback)

        context.add_widget(self._widget)

        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)

        # Bridge for opencv conversion
        self.bridge = CvBridge()

        # Set subscriber to None
        self._sub = None
        self._pub = None

    def _command_callback(self, str):
        if self._pub:
            self._pub.publish(str)

    def _image_callback(self, msg):
        """
        Called when a new sensor_msgs/Image is coming in
        :param msg: The image messaeg
        """
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(e)

        self._widget.set_image(cv_image)

    def _create_subscriber(self, topic_name):
        """
        Method that creates a subscriber to a sensor_msgs/Image topic
        :param topic_name: The topic_name
        """
        if self._sub:
            self._sub.unregister()
        self._sub = rospy.Subscriber(topic_name, Image, self._image_callback)
        rospy.loginfo("Listening to %s -- spinning .." % self._sub.name)
        self._widget.setWindowTitle("Label plugin, listening to (%s)" % self._sub.name)

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        self._create_subscriber(str(instance_settings.value("topic_name", "/camera/image_raw")))

        if self._pub is None:
            self._pub = rospy.Publisher('openstf_control_messages', String, queue_size=10)

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog