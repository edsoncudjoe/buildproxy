import os
import re
import shlex
import sys
from PyQt4 import QtCore, QtGui

from proxybuild import Ui_MainWindow

__author__ = 'Edson Cudjoe'


class MainApp(QtGui.QMainWindow):

    def __init__(self):
        super(MainApp, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.home = os.path.expanduser('~/')
        self.FFMPEG = '/usr/local/bin/ffmpeg'
        self.FFPROBE = '/usr/local/bin/ffprobe'

        self.ui.ffmpeg_opts_edit.setText('-preset fast')
        # Connections
        self.ui.open_file_btn.clicked.connect(self.open_file)
        self.ui.scan_file_btn.clicked.connect(self.scan_file)
        self.ui.set_output_dir_btn.clicked.connect(self.set_proxy_dir)
        self.ui.build_btn.clicked.connect(self.create_proxy)

        self.scan_file_process = QtCore.QProcess(self)
        self.scan_file_process.readyReadStandardError.connect(self.scan_error)
        self.process_proxy = QtCore.QProcess(self)
        self.process_proxy.readyReadStandardError.connect(self.read_std_error)
        self.process_proxy.readyReadStandardOutput.connect(self.curr_status)
        self.process_proxy.finished.connect(self.process_completed)

    def open_file(self):
        self.target_file = QtGui.QFileDialog.getOpenFileName(
            caption='Select file', directory=self.home)
        self.ui.filename_lbl.setText(self.target_file)

    def scan_file(self):
        try:
            input_file = self.target_file
            scan_args = [
                '-show_entries', 'stream=index,codec_type,codec_name',
                input_file,
            ]
            self.ui.text_browser.clear()
            self.scan_file_process.start(self.FFPROBE, scan_args)
        except AttributeError:
            self.ui.msgbx.warning(self, 'File not found',
                                  'Select a file first',
                                  QtGui.QMessageBox.Ok)

    def scan_error(self):
        self.ui.text_browser.moveCursor(QtGui.QTextCursor.Down)
        self.ui.text_browser.appendPlainText(str(
            self.scan_file_process.readAllStandardError()))

    def read_std_error(self):
        self.ui.text_browser.appendPlainText(str(
            self.process_proxy.readAllStandardError()))

    def curr_status(self):
        self.ui.text_browser.appendPlainText(str(
            self.process_proxy.readAllStandardOutput()))

    def set_proxy_dir(self):
        self.proxy_dir = QtGui.QFileDialog.getExistingDirectory(
            caption='Select directory', directory=self.home)
        self.ui.output_dir_lbl.setText(self.proxy_dir)

    def check_channels(self):
        orig_file = self.target_file

        op = self.target_file.replace(os.path.splitext(self.target_file)[1],
                                      '.mov')
        print('op: {}'.format(op)) # TODO: app does not reach this point
        option = ' ' + self.ffmpeg_opts_edit.text()
        comm = "-i '{}' -y -loglevel info {} -c:v h264 -b:v {} -crf 25 " \
               "-pix_fmt yuv420p -vf scale=320:240 -sws_flags lanczos -c:a " \
               "aac -ac 2 -b:a {} '{}{}'".format(orig_file, option,
                                                 self.VIDEO_BR, self.AUDIO_BR,
                                                 self.proxy_dir, op)
        checked = shlex.split(comm)
        print(checked)
        return checked

    def create_proxy(self):
        try:
            arguments = self.check_channels()
            print(arguments)
            proxy_dest = '{}{}'.format(self.proxy_dir, os.path.dirname(
                os.path.abspath(self.target_file)))
            if not os.path.exists(proxy_dest):
                os.makedirs(proxy_dest)
            self.ui.text_browser.clear()
            self.ui.text_browser.appendPlainText(str(arguments))
            self.process_proxy.start(self.FFMPEG, arguments)
            self.ui.progress_bar.setRange(0, 0)
            self.ui.build_btn.setDisabled(True)
        except AttributeError:
            self.ui.msgbx.warning(self, 'File not found', 'Check that an input file'
                                                     '\nand proxy directory '
                                                     'have both been selected',
                             QtGui.QMessageBox.Ok)


    def process_completed(self):
        self.ui.progress_bar.setRange(0, 1)
        self.ui.build_btn.setEnabled(True)
        self.msg.information(self, 'Complete',
                             'Finished conversion')

def main():
    app = QtGui.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
