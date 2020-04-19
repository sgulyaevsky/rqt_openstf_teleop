cmake_minimum_required(VERSION 2.8.3)
project(rqt_openstf_teleop)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  rospy
  rqt_gui_py
)

catkin_python_setup()

catkin_package()

install(FILES plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(PROGRAMS
  scripts/rqt_openstf_teleop
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
