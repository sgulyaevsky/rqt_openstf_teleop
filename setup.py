from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rqt_openstf_teleop'],
    package_dir={'': 'src'},
)

setup(**d)