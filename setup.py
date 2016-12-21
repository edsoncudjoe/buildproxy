from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True,
           'includes': ['sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui'],
           'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork',
                        'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql',
                        'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml',
                        'PyQt4.phonon']
           }

setup(
    name='ProxyBuilder',
    version='1.0.1',
    description='Create 320x240 proxy video files',
    date='21-Dec-2016',
    url='https://github.com/edsoncudjoe/buildproxy',

    author='Edson Cudjoe',
    author_email='mail@edsoncudjoe.com',
    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Natural Language :: English',
        'Topic :: Multimedia :: Video :: Conversion',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='python python3 pyqt4 ffmpeg',

    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
