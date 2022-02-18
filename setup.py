from setuptools import setup

setup(name='damnsshmanager',
      version='0.2.3',
      description='The simplest ssh cli agent one is able to find',
      url='git@github.com:captain-proton/damnsshmanager.git',
      author='Nils Verheyen',
      author_email='nils@ungerichtet.de',
      entry_points={
          'console_scripts': [
              'dsm=damnsshmanager.cli:main',
          ],
      },
      include_package_data=True,
      license='GNU GPLv3',
      packages=[
          'damnsshmanager',
          'damnsshmanager.ssh',
      ],
      package_data={
          'damnsshmanager': ['damnfiles/messages.ini'],
      },
      python_requires='>=3',
      zip_safe=False)
