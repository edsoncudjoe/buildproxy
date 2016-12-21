import os
import re
import shlex
import sys
from PyQt4 import QtCore, QtGui


class ProxyBuild(QtGui.QWidget):

    def __init__(self):
        super(ProxyBuild, self).__init__()

        self.initUI()
        self.home = os.path.expanduser('~/')

        self.FILETYPES = ('.mov', '.mxf', '.mpg', '.avi')
        self.FFMPEG = '/usr/local/bin/ffmpeg'
        self.FFPROBE = '/usr/local/bin/ffprobe'
        self.CRF_VALUE = '25'
        self.VIDEO_BR = '100k'
        self.AUDIO_BR = '48k'
        self.PRESET = 'fast'

    def initUI(self):

        self.file_input_lbl = QtGui.QLabel('Input file', self)
        self.proxy_location_lbl = QtGui.QLabel('Proxy location', self)
        self.get_target_btn = QtGui.QPushButton('Browse')
        self.scan_btn = QtGui.QPushButton('Scan')
        self.set_proxy_location_btn = QtGui.QPushButton('Proxy directory')
        self.build_btn = QtGui.QPushButton('Build')
        self.progress = QtGui.QProgressBar()
        self.progress.setRange(0, 1)
        self.text_browser = QtGui.QPlainTextEdit()
        self.text_browser.setReadOnly(True)
        self.text_browser.setWordWrapMode(
            QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.msg = QtGui.QMessageBox()

        self.options_lbl = QtGui.QLabel('FFMpeg Options: ', self)
        self.options_bar = QtGui.QLineEdit()
        self.options_bar.setText('-preset fast')

        # tooltips
        self.get_target_btn.setToolTip('Open a new file')
        self.scan_btn.setToolTip('Scan your file for media config')
        self.set_proxy_location_btn.setToolTip('Choose where to save the '
                                               'converted proxy file')
        self.options_lbl.setToolTip('Add extra FFMpeg options')
        self.options_bar.setToolTip('Add extra FFMpeg options')
        self.build_btn.setToolTip('Build proxy media file')

        # signals
        self.get_target_btn.clicked.connect(self.select_target_dir)
        self.set_proxy_location_btn.clicked.connect(self.set_proxy_dir)

        QtCore.QObject.connect(self.build_btn, QtCore.SIGNAL('clicked()'),
                               self.create_proxy)
        QtCore.QObject.connect(self.scan_btn, QtCore.SIGNAL('clicked()'),
                               self.scan_file)
        self.process_proxy = QtCore.QProcess(self)
        self.process_proxy.readyReadStandardError.connect(self.read_std_error)
        self.process_proxy.readyReadStandardOutput.connect(self.curr_status)
        self.process_proxy.finished.connect(self.process_completed)
        self.scan_process = QtCore.QProcess(self)
        self.scan_process.readyReadStandardError.connect(self.scan_error)

        main_grid = QtGui.QGridLayout()
        main_grid.setSpacing(10)

        main_grid.addWidget(self.get_target_btn, 2, 0)
        main_grid.addWidget(self.file_input_lbl, 2, 1, 1, 3)
        main_grid.addWidget(self.scan_btn, 2, 4)
        main_grid.addWidget(self.proxy_location_lbl, 3, 1, 1, 3)
        main_grid.addWidget(self.set_proxy_location_btn, 3, 0)

        main_grid.addWidget(self.options_lbl, 5, 0)
        main_grid.addWidget(self.options_bar, 5, 1)

        main_grid.addWidget(self.build_btn, 6, 0, 2, 5)
        main_grid.addWidget(self.progress, 7, 0, 1, 5)
        main_grid.addWidget(self.text_browser, 8, 0, 12, 10)

        self.setLayout(main_grid)
        self.setGeometry(700, 700, 600, 100)
        self.setFixedSize(1200, 700)
        self.setWindowTitle('Proxy-Builder')

    def select_target_dir(self):
        self.target_file = os.path.expanduser(
            QtGui.QFileDialog.getOpenFileName(
                caption='Select file', directory=self.home))
        self.file_input_lbl.setText(self.target_file)

    def set_proxy_dir(self):
        self.proxy_dir = QtGui.QFileDialog.getExistingDirectory(caption='Select '
                                                                    'directory',
                                                            directory=self.home)
        self.proxy_location_lbl.setText(self.proxy_dir)

    def scan_file(self):
        try:
            inpf = self.target_file
            scan_args = [
                '-show_entries', 'stream=index,codec_type,codec_name', inpf,
            ]
            self.text_browser.clear()
            self.scan_process.start(self.FFPROBE, scan_args)
        except AttributeError:
            self.msg.warning(self, 'File not found', 'Select a file first',
                             QtGui.QMessageBox.Ok)

    def check_channels(self):
        orig_file = self.target_file
        op = self.target_file.replace(os.path.splitext(self.target_file)[1],
                                          '.mov')
        option = ' ' + self.options_bar.text()
        comm = "-i '{}' -y -loglevel info {} -c:v h264 -b:v {} -crf 25 " \
               "-pix_fmt yuv420p -vf scale=320:240 -sws_flags lanczos -c:a " \
               "aac -ac 2 -b:a {} '{}{}'".format(orig_file, option,
                                                 self.VIDEO_BR, self.AUDIO_BR,
                                                 self.proxy_dir, op)
        checked = shlex.split(comm)
        return checked

    def create_proxy(self):
        try:
            arguments = self.check_channels()
            print(arguments)
            proxy_dest = '{}{}'.format(self.proxy_dir, os.path.dirname(
                os.path.abspath(self.target_file)))
            if not os.path.exists(proxy_dest):
                os.makedirs(proxy_dest)
            self.text_browser.clear()
            self.text_browser.appendPlainText(str(arguments))
            self.process_proxy.start(self.FFMPEG, arguments)
            self.progress.setRange(0, 0)
            self.build_btn.setDisabled(True)
        except AttributeError:
            self.msg.warning(self, 'File not found', 'Check that an input file'
                                                     '\nand proxy directory '
                                                     'have both been selected',
                             QtGui.QMessageBox.Ok)

    def read_std_error(self):
        self.text_browser.appendPlainText(str(
            self.process_proxy.readAllStandardError()))

    def curr_status(self):
        self.text_browser.appendPlainText(str(
            self.process_proxy.readAllStandardOutput()))

    def scan_error(self):
        self.text_browser.moveCursor(QtGui.QTextCursor.Down)
        self.text_browser.appendPlainText(str(
            self.scan_process.readAllStandardError(), 'utf-8'))

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
