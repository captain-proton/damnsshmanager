from setuptools import setup

setup(name='damnsshmanager',
      version='0.2.3',
      description='The simplest ssh cli agent one is able to find',
      url='http://github.com/captain-proton/damnsshmanager',
      author='Nils',
      author_email='nils@hindenbug.de',
      entry_points={
          'console_scripts': [
              'dsm=damnsshmanager.cli:main',
          ],
      },
      include_package_data=True,
      license='MIT',
      packages=['damnsshmanager'],
      package_data={
          'damnsshmanager': ['damnfiles/messages.ini'],
      },
      python_requires='>=3',
      zip_safe=False)
