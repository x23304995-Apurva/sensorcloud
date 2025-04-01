import os
import shutil

# Define the paths for the original and new directories
original_dir = './aws_services'  # Path to your current AWS services directory
pypi_package_dir = './sensorcloud_services'  # New directory for PyPI package
pypi_services_dir = os.path.join(pypi_package_dir, 'aws_services')

# List of files you want to copy to your PyPI package
files_to_copy = [
    'sns_handler.py',  # Only the sns_handler is used in `views.py`
    # Add other files if needed, e.g. 'sqs_handler.py', 'dynamodb_handler.py'
]

# Create the new PyPI package directory
os.makedirs(pypi_services_dir, exist_ok=True)

# Copy necessary files to the new directory
for file_name in files_to_copy:
    src_file = os.path.join(original_dir, file_name)
    if os.path.exists(src_file):
        dest_file = os.path.join(pypi_services_dir, file_name)
        shutil.copy(src_file, dest_file)
        print(f"Copied: {file_name}")
    else:
        print(f"Warning: {file_name} not found in {original_dir}")

# Create necessary PyPI package structure
os.makedirs(pypi_package_dir, exist_ok=True)

# Copy setup.py, requirements.txt, and other necessary files
with open(os.path.join(pypi_package_dir, 'setup.py'), 'w') as f:
    f.write("""from setuptools import setup, find_packages

setup(
    name='sensorcloud_services',
    version='0.1',
    packages=find_packages(include=['aws_services']),
    install_requires=[
        'boto3',  # Add other dependencies if needed
    ],
)
""")
print("Created setup.py")

with open(os.path.join(pypi_package_dir, 'README.md'), 'w') as f:
    f.write("# sensorcloud_services\nThis is a custom library to interact with AWS services.\n")
print("Created README.md")

with open(os.path.join(pypi_package_dir, 'requirements.txt'), 'w') as f:
    f.write("boto3\n")  # Add other dependencies if needed
print("Created requirements.txt")

# Create an empty LICENSE file
with open(os.path.join(pypi_package_dir, 'LICENSE'), 'w') as f:
    f.write("MIT License\n")
print("Created LICENSE file")

# Create __init__.py in aws_services directory
with open(os.path.join(pypi_services_dir, '__init__.py'), 'w') as f:
    f.write("from .sns_handler import SNSHandler\n")
print("Created __init__.py")

# Done
print("PyPI package structure is ready! You can now upload the package to PyPI.")
