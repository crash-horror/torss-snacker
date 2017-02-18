#!/usr/bin/env python3
# tor-snacker.pyw
# github.com/crash-horror

import os
import sys
import subprocess
import time
import socket
import logging
import webbrowser
import codecs
import configparser
import feedparser
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import QTimer, Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QListWidget, QApplication, QMainWindow, QSystemTrayIcon,
                             QWidget, QSizePolicy, QMenu, QAction, QListWidgetItem,
                             QCheckBox, qApp, QMessageBox)


version = 0.297
title = 'ToRss Snacker'

socket.setdefaulttimeout(5)

# file paths
myfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")
subspath = myfilepath + "tor.subs.txt"
urlpath = myfilepath + "tor.rsslist.txt"

CP = configparser.ConfigParser()
CP.read(myfilepath + 'tor.config.ini', 'utf8')

# make the lists from config.ini
green_tor = CP.get('options', 'green', fallback='rarbg, rartv').lower().replace(' ', '').split(',')
purple_tor = CP.get('options', 'purple', fallback='cm8').lower().replace(' ', '').split(',')
red_tor = CP.get('options', 'red', fallback='yts').lower().replace(' ', '').split(',')
yellow_tor = CP.get('options', 'yellow', fallback='news, ελλάδα').lower().replace(' ', '').split(',')
gray_tor = CP.get('options', 'gray', fallback='eztv').lower().replace(' ', '').split(',')

# remove empty strings from the lists
green_tor = list(filter(None, green_tor))
purple_tor = list(filter(None, purple_tor))
red_tor = list(filter(None, red_tor))
yellow_tor = list(filter(None, yellow_tor))
gray_tor = list(filter(None, gray_tor))

refreshinterval = int(CP.get('options', 'refreshinterval', fallback='5'))

# set minimum refresh to 1 minute
if refreshinterval < 1:
    refreshinterval = 1


confighelpstring = """# INSTRUCTIONS!
#-------------------------------------------------------------
# set color filters, separated by commas.
# green & purple is applied to RSS feed text body only.
# purple is applied to RSS feed text body only.
# red, yellow & gray applies to the RSS title.
# match only dot links with onlydotmatch = yes
# fetch new feeds every refreshinterval = 5 in minutes.
#-------------------------------------------------------------

"""



class mySystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):

        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)

        infoaction = self.menu.addAction(QIcon('stuff/info.png'), "About")
        infoaction.triggered.connect(myGUI.info_action)

        exitaction = self.menu.addAction(QIcon('stuff/exit-1.png'), "Exit")
        exitaction.triggered.connect(qApp.quit)

        self.setContextMenu(self.menu)
        self.setToolTip(title + ' v' + str(version))



class Worker(QObject):

    finished = pyqtSignal()
    feedready = pyqtSignal(tuple)
    addclock = pyqtSignal(str)
    addwarning = pyqtSignal(str)
    statusupdate = pyqtSignal()


    @pyqtSlot()
    def run_loop(self): # A slot takes no params

        refreshtime = 60 * refreshinterval # seconds
        subscribe_tor = myData.return_subscriptions()

        getlist = myData.get_xml(myData.return_url_list())

        t0 = 0.0

        recentlist = []
        for initial in getlist:
            recentlist.append(initial)
            self.feedready.emit(initial)

        self.statusupdate.emit()

        while True:
            time.sleep(refreshtime)

            oldurls = myData.return_url_list()
            newurls = myData.get_url_list()
            if oldurls != newurls:
                self.addwarning.emit('RSS URLs file updated!')

            newlist = myData.get_xml(myData.return_url_list())

            for feed in newlist:
                if feed not in recentlist:

                    checksubs = myData.get_subscriptions()
                    if checksubs != subscribe_tor:
                        subscribe_tor = checksubs
                        self.addwarning.emit('Subscriptions file updated!')

                    self.feedready.emit(feed)
                    recentlist.append(feed)

            self.statusupdate.emit()

            t1 = time.time()
            if t1 - t0 > 60 * 10: # seconds
                self.addclock.emit(time_string())
                t0 = time.time()



class MyDataClass():

    def __init__(self):
        self.subscribe_tor = []
        self.feed_list = []
        self.urllist = []
        self.onlydotmatch = CP.getboolean('options', 'onlydotmatch', fallback=False)
        self.get_subscriptions()
        self.get_url_list()


    def get_url_list(self):
        urllist = []
        with codecs.open(urlpath, "r", 'utf-8', errors='ignore') as readurllist:
            thelines = readurllist.readlines()
        for i in thelines:
            if len(i) > 1:
                urllist.append(i.strip())
        self.urllist = urllist
        return self.urllist


    def get_subscriptions(self):
        sublist = []
        with codecs.open(subspath, "r", 'utf-8', errors='ignore') as readtodosubs:
            thelines = readtodosubs.readlines()
        for i in thelines:
            i = i.lower()

            # subscribed everything
            if not self.onlydotmatch:
                i = i.strip()
                if i != '':
                    sublist.append(i + ' ')

            # subscribed dot matched only
            i = ".".join(i.split()) + '.'  # spaces to dots + a dot
            if i.strip() != '.':
                sublist.append(i)

        self.subscribe_tor = sublist
        return self.subscribe_tor


    def get_xml(self, _alist):
        ls = []
        for url in _alist:
            counter = 0
            try:
                d = feedparser.parse(url)
            except:
                print(url, '\nNot accessible!')
                logger.exception('get_xml exception')
            while True:

                try:
                    magnet = d.entries[counter].torrent_magneturi
                except AttributeError:
                    magnet = None
                except IndexError:
                    break

                try:
                    link = d.entries[counter].link
                except AttributeError:
                    link = None
                except IndexError:
                    break

                if 'magnet:?' in link:
                    magnet = link

                try:
                    ls.append((d.entries[counter].published, d.feed.title, d.entries[counter].title, link, magnet))
                except IndexError:  # check until end of feed
                    break
                except AttributeError:
                    logger.exception('get_xml exception AttributeError')
                else:
                    counter += 1


        self.feed_list = ls[::-1]
        return self.feed_list


    def return_subscriptions(self):
        return self.subscribe_tor


    def return_url_list(self):
        return self.urllist



class MyMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowOpacity(0.9)
        self.deffontsize = 9
        self.autoscroll = True
        self.auto_open_magnets = True

        # 1 - create Worker and Thread inside the Form
        self.obj = Worker()  # no parent!
        self.thread = QThread()  # no parent!
        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.obj.feedready.connect(self.populate_me)
        self.obj.addclock.connect(self.add_clock)
        self.obj.addwarning.connect(self.add_warning)
        self.obj.statusupdate.connect(self.change_title)
        # 3 - Move the Worker object to the Thread object
        self.obj.moveToThread(self.thread)
        # 4 - Connect Worker Signals to the Thread slots
        self.obj.finished.connect(self.thread.quit)
        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.obj.run_loop)
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)
        # 6 - Start the thread
        self.thread.start()
        # 7 - Start the form
        self.initUI()



    def initUI(self):
        self.mylistwidget = QListWidget()
        self.mylistwidget.itemClicked.connect(self.list_item_clicked)
        self.mylistwidget.setStyleSheet("""
                                            QListWidget {
                                                        border-style: none;
                                                        color: lightgray;
                                                        background: rgba(0, 0, 0, 255);
                                                        }
                                            QListWidget::item:hover {
                                                        background-color: #303030;
                                                        }
                                            QListWidget::item:selected:active {
                                                        background-color: #505050;
                                                        }
                                            QListWidget::item:selected:!active {
                                                        background-color: #505050;
                                                        }
                                                            """)

        plusaction = QAction(QIcon('stuff/plus.png'), 'Larger Font\nCtrl [=]', self)
        plusaction.setShortcut('Ctrl+=')
        plusaction.triggered.connect(self.plus_action)

        minusaction = QAction(QIcon('stuff/minus.png'), 'Smaller Font\nCtrl [-]', self)
        minusaction.setShortcut('Ctrl+-')
        minusaction.triggered.connect(self.minus_action)

        editaction = QAction(QIcon('stuff/edit.png'), 'Edit Subscriptions\nCtrl [E]', self)
        editaction.setShortcut('Ctrl+e')
        editaction.triggered.connect(self.edit_action)

        linkaction = QAction(QIcon('stuff/link.png'), 'Edit RSS URLs\nCtrl [U]', self)
        linkaction.setShortcut('Ctrl+u')
        linkaction.triggered.connect(self.link_action)

        scrollaction = QCheckBox('Scroll', self)
        scrollaction.toggle()
        scrollaction.setShortcut('Ctrl+s')
        scrollaction.stateChanged.connect(self.scroll_action_toggle)

        magnetaction = QCheckBox('Mags', self)
        magnetaction.toggle()
        magnetaction.stateChanged.connect(self.magnet_action_toggle)

        dotaction = QCheckBox('DotOnly', self)
        if myData.onlydotmatch:
            dotaction.toggle()
        dotaction.stateChanged.connect(self.dot_action_toggle)

        infoaction = QAction(QIcon('stuff/info.png'), 'About', self)
        infoaction.triggered.connect(self.info_action)

        self.toolbar = self.addToolBar('Buttons!')
        self.toolbar.addAction(plusaction)
        self.toolbar.addAction(minusaction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(editaction)
        self.toolbar.addAction(linkaction)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(self.spacer)

        self.toolbar.addWidget(dotaction)
        self.toolbar.addWidget(magnetaction)
        self.toolbar.addWidget(scrollaction)
        self.toolbar.addAction(infoaction)

        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))
        self.resize(1180, 500)
        self.setWindowTitle(title + ' v' + str(version))
        self.setWindowIcon(QIcon('stuff/tor.png'))
        self.setCentralWidget(self.mylistwidget)
        self.show()


    def change_title(self):
        self.setWindowTitle(title + ' v' + str(version) + ' @ ' + time.strftime("%X") + ' (Updated every ' + str(refreshinterval) + ' minutes)')


    def list_item_clicked(self, item):
        if len(item.text()) > 10:
            if item.data(201) is not None and self.auto_open_magnets:
                webbrowser.open(item.data(201))
            else:
                webbrowser.open(item.data(200))


    def populate_me(self, _feed):

        if _feed[4] is not None:
            if _feed[3] == _feed[4]:
                magprefix = '** '
            else:
                magprefix = '* '
        else:
            magprefix = ''

        i = QListWidgetItem(magprefix + _feed[2] + '   (' + _feed[1] + ')')
        i.setData(200, _feed[3])
        i.setData(201, _feed[4])

        # HD
        if "720" in _feed[2] or "1080" in _feed[2]:
            boldHD = 55
        else:
            boldHD = 0

        i.setForeground(QColor(200 + boldHD, 200 + boldHD, 200 + boldHD))

        # red
        if any(x in str.lower(_feed[1]) for x in red_tor):
            i.setForeground(QColor(200 + boldHD, 0, 0))

        # gray
        if any(y in str.lower(_feed[1]) for y in gray_tor):
            i.setForeground(QColor(150 + boldHD, 150 + boldHD, 150 + boldHD))

        # green
        # green for inside string search, not on feed title!
        if any(y in str.lower(_feed[2]) for y in green_tor):
            i.setForeground(QColor(0, 200 + boldHD, 0))

        # purple
        # purple for inside string search, not on feed title!
        if any(y in str.lower(_feed[2]) for y in purple_tor):
            # i.setForeground(QColor(200 + boldHD, 0, 200 + boldHD))  # <--- bold capable alternative
            i.setForeground(QColor(250, 0, 250))

        # yellow
        if any(y in str.lower(_feed[1]) for y in yellow_tor):
            i.setForeground(QColor(150, 100, 0))

        # subscribed
        if any(z in str.lower(_feed[2]) for z in myData.return_subscriptions()):
            i.setBackground(QColor(0, 0, 250))

        self.mylistwidget.addItem(i)
        self.scroll_action()



    def scroll_action(self):
        if self.autoscroll:
            QTimer.singleShot(0, self.mylistwidget.scrollToBottom)


    def scroll_action_toggle(self, state):
        if state == Qt.Checked:
            self.autoscroll = True
        else:
            self.autoscroll = False


    def magnet_action_toggle(self, state):
        if state == Qt.Checked:
            self.auto_open_magnets = True
        else:
            self.auto_open_magnets = False


    def dot_action_toggle(self, state):
        if state == Qt.Checked:
            myData.onlydotmatch = True
            CP.set('options', 'onlydotmatch', 'yes')
        else:
            myData.onlydotmatch = False
            CP.set('options', 'onlydotmatch', 'no')
        write_config_ini()


    def add_clock(self, _time):
        t = QListWidgetItem(_time)
        self.mylistwidget.addItem(t)
        self.scroll_action()


    def plus_action(self):
        self.deffontsize += 2
        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))


    def minus_action(self):
        self.deffontsize -= 2
        if self.deffontsize < 9:
            self.deffontsize = 9
        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))


    def edit_action(self):
        if sys.platform == "win32":
            os.startfile(subspath)
        else:
            subprocess.call(["xdg-open", subspath])


    def link_action(self):
        if sys.platform == "win32":
            os.startfile(urlpath)
        else:
            subprocess.call(["xdg-open", urlpath])


    def info_action(self):
        QMessageBox.about(self, "About '" + title + "'",
                """
                <h3>Usage instructions and stuff:</h3>
                <ul>
                    <li><b>Click</b> on a list item to open browser or magnet link.</li>
                    <li>One <b>*</b> means the feed has magnet link and info webpage.</li>
                    <li>Two <b>**</b> means the feed has <b>only</b> magnet link.</li>
                    <li><b>High Def</b> links appear brighter (720p & 1080p).</li>
                    <li>If <b>DotOnly</b> is selected, the list will only highlight items with.dots.instead.of.spaces.like.this.</li>
                    <li>If <b>Mags</b> is selected, clicking will prioritize <b>direct magnet download</b> instead of webpage.</li>
                    <li>If <b>Scroll</b> is selected, the list will auto scroll on update.</li>
                    <br>
                    <li><b>Edit Subscriptions</b> to blue-highlight your favorites.</li>
                    <li><b>Edit RSS URLs</b> to set your RSS sources (one per line).</li>
                    <br>
                    <li>Edit <b>tor.config.ini</b> file to set options:
                        <ul>
                            <li>Green list items.</li>
                            <li>Red list items.</li>
                            <li>Yellow list items.</li>
                            <li>Gray list items.</li>
                            <li>Set the <b>refresh interval</b> (default = 5 minutes).</li>
                        </ul>
                    </li>
                </ul>
                <p>
                    <b>Disclaimer:</b> Use this Software at your own risk, downloading copyrighted material is illegal.
                </p>""")


    def add_warning(self, _text):
        w = QListWidgetItem(_text)
        w.setForeground(QColor(255, 255, 255))
        w.setBackground(QColor(255, 0, 0))
        self.mylistwidget.addItem(w)
        self.scroll_action()


    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()



def time_string():
    return "    " + time.strftime("%H:%M")


def uncaught_exception_handler(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def write_config_ini():
    with open('tor.config.ini', 'w') as configfile:
        configfile.write(confighelpstring)
        CP.write(configfile)




if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(filename='_error.log', format='%(asctime)s :%(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logger.info('Starting...')
    sys.excepthook = uncaught_exception_handler

    myData = MyDataClass()

    app = QApplication(sys.argv)
    myGUI = MyMainWindow()

    trayIcon = mySystemTrayIcon(QIcon("stuff/tor.png"), myGUI)
    trayIcon.show()
    trayIcon.activated.connect(myGUI.tray_icon_clicked)

    app.aboutToQuit.connect(trayIcon.hide)
    sys.exit(app.exec_())






# Notes:
"""
pyinstaller --paths C:\Python35\Lib\site-packages\PyQt5\Qt\bin -w -F --icon=stuff/tor.ico tor-snacker.pyw
"""
