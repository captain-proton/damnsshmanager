from setuptools import setup

setup(name='damnsshmanager',
      version='0.1',
      description='The simplest ssh cli agent one is able to find',
      url='http://github.com/captain-proton/damnsshmanager',
      author='Captain proton',
      scripts=['bin/dsm'],
      include_package_data=True,
      license='MIT',
      packages=['damnsshmanager'],
      zip_safe=False)
