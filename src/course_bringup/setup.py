"""Install the course bringup package manifest and launch file."""

from setuptools import setup


package_name = 'course_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/course_bringup']),
        ('share/course_bringup', ['package.xml']),
        ('share/course_bringup/launch', ['launch/patrol.launch.py']),
    ],
    maintainer='TihonSotnikov',
    maintainer_email='t.sotnikov@g.nsu.ru',
    description='Namespaced patrol, sensor QoS and MCAP recording for PR05',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
)
