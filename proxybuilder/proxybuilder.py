import os
import sys
from PyQt4 import QtCore, QtGui


class ProxyBuild(QtGui.QWidget):

    def __init__(self):
        super(ProxyBuild, self).__init__()

        self.initUI()
        self.home = os.path.expanduser('~/')

        self.FILETYPES = ('.mov', '.mxf', '.mpg', '.avi')
        self.FFMPEG = '/usr/local/bin/ffmpeg'
        self.CRF_VALUE = '25'
        self.VIDEO_BR = '100k'
        self.AUDIO_BR = '48k'
        self.PRESET = 'ultrafast'

    def initUI(self):

        self.file_input_lbl = QtGui.QLabel('Input file', self)
        self.proxy_location_lbl = QtGui.QLabel('Proxy location', self)
        self.get_target_btn = QtGui.QPushButton('Target file')
        self.set_proxy_location_btn = QtGui.QPushButton('Proxy directory')
        self.build_btn = QtGui.QPushButton('Build')
        self.progress = QtGui.QProgressBar()
        self.progress.setRange(0, 1)
        self.msg = QtGui.QMessageBox()

        self.get_target_btn.clicked.connect(self.select_target_dir)
        self.set_proxy_location_btn.clicked.connect(self.set_proxy_dir)

        QtCore.QObject.connect(self.build_btn, QtCore.SIGNAL('clicked()'),
                               self.create_proxy)
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardError.connect(self.read_std_error)
        self.process.readyReadStandardOutput.connect(self.curr_status)
        self.process.finished.connect(self.process_completed)

        main_grid = QtGui.QGridLayout()
        main_grid.setSpacing(10)

        main_grid.addWidget(self.get_target_btn, 2, 0)
        main_grid.addWidget(self.file_input_lbl, 2, 1, 1, 3)
        main_grid.addWidget(self.proxy_location_lbl, 3, 1, 1, 3)
        main_grid.addWidget(self.set_proxy_location_btn, 3, 0)
        main_grid.addWidget(self.build_btn, 4, 0, 2, 4)
        main_grid.addWidget(self.progress, 6, 0, 1, 4)

        self.setLayout(main_grid)
        self.setGeometry(300, 700, 600, 100)
        self.setFixedSize(610, 200)
        self.setWindowTitle('Proxy-Builder')

    def select_target_dir(self):
        self.target_file = QtGui.QFileDialog.getOpenFileName(caption='Select '
                                                                    'file',
                                                            directory=self.home)
        self.file_input_lbl.setText(self.target_file)

    def set_proxy_dir(self):
        self.proxy_dir = QtGui.QFileDialog.getExistingDirectory(caption='Select '
                                                                    'directory',
                                                            directory=self.home)
        self.proxy_location_lbl.setText(self.proxy_dir)

    def create_proxy(self):
        orig_file = os.path.expanduser(self.target_file)
        op = self.target_file.replace(os.path.splitext(self.target_file)[1],
                                      '.mp4')
        arguments = [
            '-progress', 'progress.txt',
            '-i', orig_file,
            '-y', '-loglevel', 'verbose',
            '-map', '0:v',
            '-map', '0:0',
            '-map', '0:1',
            '-c:v', 'h264',
            '-b:v', self.VIDEO_BR,
            '-crf', self.CRF_VALUE,
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=320:240',
            '-sws_flags', 'lanczos',
            '-c:a', 'aac',
            '-ac', '2',
            '-b:a', self.AUDIO_BR,
            '{}{}'.format(self.proxy_dir, op)
        ]
        proxy_dest = '{}{}'.format(self.proxy_dir, os.path.dirname(os.path.abspath(self.target_file)))
        if not os.path.exists(proxy_dest):
            os.makedirs(proxy_dest)
        print(arguments)
        self.process.start(self.FFMPEG, arguments)
        self.progress.setRange(0, 0)
        self.build_btn.setDisabled(True)

    def read_std_error(self):
        print(str(self.process.readAllStandardError()))

    def curr_status(self):
        print(str(self.process.readAllStandardOutput()))

    def process_completed(self):
        self.progress.setRange(0, 1)
        self.build_btn.setEnabled(True)
        self.msg.information(self, 'Complete',
                             'Finished conversion')


def main():
    app = QtGui.QApplication(sys.argv)
    m = ProxyBuild()
    m.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
