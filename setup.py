from setuptools import setup

setup(name='damnsshmanager',
      version='0.1.2',
      description='The simplest ssh cli agent one is able to find',
      url='http://github.com/captain-proton/damnsshmanager',
      author='Nils',
      author_email='nils@hindenbug.de',
      scripts=['bin/dsm'],
      include_package_data=True,
      license='MIT',
      packages=['damnsshmanager'],
      package_data={
          'damnfiles': ['messages.ini'],
      },
      zip_safe=False)
