from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(name='pyWoodway',
      version='0.2.1',
      url='https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyWoodway',
      author='Walker Arce',
      author_email='walker.arce@unmc.edu',
      description='Communicate with your Woodway treadmill in your Python scripts.',
      keywords='Woodway treadmill biomechanics',
      long_description=readme,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.8'
      ],
      long_description_content_type="text/markdown",
      # packages=find_packages(),
      zip_safe=False,
      license='MIT',
      include_package_data=True,
      packages=['pywoodway'],
      install_requires=[
            'pyserial'
      ],
      )

# python setup.py bdist_wheel
# pip3 install pdoc3
# pdoc --html --output-dir docs pywoodway
# https://ftdichip.com/drivers/
