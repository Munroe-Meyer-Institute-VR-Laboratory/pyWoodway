from setuptools import setup, find_packages

setup(name='pyWoodway',
      version='0.1',
      url='https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyWoodway',
      author='Walker Arce',
      author_email='walker.arce@unmc.edu',
      description='Communicate with your Woodway treadmill in your Python scripts.',
      packages=find_packages(),
      long_description=open('README.md').read(),
      zip_safe=False)

# python setup.py bdist_wheel
# pip3 install pdoc3
# pdoc --html --output-dir docs pywoodway
# https://ftdichip.com/drivers/
