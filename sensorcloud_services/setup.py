from setuptools import setup, find_packages

setup(
    name='sensorcloud_services',
    version='0.2',
    packages=find_packages(include=['aws_services']),
    install_requires=[
        'boto3',  # Add other dependencies if needed
    ],
)
