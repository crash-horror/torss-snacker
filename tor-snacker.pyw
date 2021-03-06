# github.com/crash-horror
# tor-snacker.pyw

# pylint: disable=c

import os
import sys
import subprocess
import time
import socket
import logging
import webbrowser
import codecs
from multiprocessing.dummy import Pool as ThreadPool
import pickle
import feedparser
# pylint: disable=no-name-in-module
from PyQt5.QtGui import QIcon, QFont, QColor, QIntValidator
from PyQt5.QtCore import QTimer, Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QListWidget, QApplication, QMainWindow, QSystemTrayIcon,
                             QWidget, QSizePolicy, QMenu, QAction, QListWidgetItem,
                             QCheckBox, qApp, QMessageBox, QLineEdit, QDialog,
                             QFormLayout, QDialogButtonBox)




version = 0.378
title = 'ToRss Snacker'

socket.setdefaulttimeout(5)

# file paths
myfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")
subspath = myfilepath + "tor.subs.txt"
urlpath = myfilepath + "tor.rsslist.txt"
picklepath = myfilepath + "data.pkl"



class PickleData:

    def __init__(self):
        # todo clean this mess, maybe...
        self.greendefault = ['rarbg', 'rartv']
        self.purpledefault = ['cm8', 'fgt']
        self.reddefault = ['yts',]
        self.yellowdefault = ['news', 'ελλάδα', 'alert']
        self.greydefault = ['eztv',]
        self.refreshdefault = 5
        self.fontdefault = 19
        self.opacitydefault = 1.0
        self.check_if_pickle_file()

    def check_if_pickle_file(self):
        if os.path.isfile(picklepath):
            with open(picklepath, 'rb') as f:
                self.pickledict = pickle.load(f)
        else:
            self.create_default_dict()
            with open(picklepath, 'wb') as f:
                pickle.dump(self.pickledict, f)
        self.set_temp_variables()

    def create_default_dict(self):
        self.pickledict = {}
        self.pickledict['green'] = self.greendefault
        self.pickledict['purple'] = self.purpledefault
        self.pickledict['red'] = self.reddefault
        self.pickledict['yellow'] = self.yellowdefault
        self.pickledict['grey'] = self.greydefault
        self.pickledict['refresh'] = self.refreshdefault
        self.pickledict['fontsize'] = self.fontdefault
        self.pickledict['opacity'] = self.opacitydefault

    def set_temp_variables(self):
        self.greentemp = self.pickledict['green']
        self.purpletemp = self.pickledict['purple']
        self.redtemp = self.pickledict['red']
        self.yellowtemp = self.pickledict['yellow']
        self.greytemp = self.pickledict['grey']
        self.refreshtemp = self.pickledict['refresh']

    def write_pickle_data(self):
        with open(picklepath, 'wb') as f:
            pickle.dump(self.pickledict, f)

    def opacity_setting(self):
        return self.pickledict['opacity']

    def font_setting(self):
        return self.pickledict['fontsize']

    def green_tor(self):
        return self.pickledict['green']

    def purple_tor(self):
        return self.pickledict['purple']

    def red_tor(self):
        return self.pickledict['red']

    def yellow_tor(self):
        return self.pickledict['yellow']

    def grey_tor(self):
        return self.pickledict['grey']

    def refresh_setting(self):
        return self.pickledict['refresh']





class OptionDialog(QDialog):
    def __init__(self, parent=None):
        super(OptionDialog, self).__init__(parent)

        self.setWindowTitle('Options')
        self.setFont(QFont("Arial", 12))

        flo = QFormLayout()

        self.redoption = QLineEdit(self)
        self.redoption.setText(list_to_string(mySettings.red_tor()))
        self.redoption.textChanged.connect(self.redtextchanged)
        flo.addRow("Red (Feed title)", self.redoption)

        self.greyoption = QLineEdit(self)
        self.greyoption.setText(list_to_string(mySettings.grey_tor()))
        self.greyoption.textChanged.connect(self.greytextchanged)
        flo.addRow("Grey (Feed title)", self.greyoption)

        self.yellowoption = QLineEdit(self)
        self.yellowoption.setText(list_to_string(mySettings.yellow_tor()))
        self.yellowoption.textChanged.connect(self.yellowtextchanged)
        flo.addRow("Yellow (Feed title)", self.yellowoption)

        self.greenoption = QLineEdit(self)
        self.greenoption.setText(list_to_string(mySettings.green_tor()))
        self.greenoption.textChanged.connect(self.greentextchanged)
        flo.addRow("Green (Feed text)", self.greenoption)

        self.purpleoption = QLineEdit(self)
        self.purpleoption.setText(list_to_string(mySettings.purple_tor()))
        self.purpleoption.textChanged.connect(self.purpletextchanged)
        flo.addRow("Purple (Feed text)", self.purpleoption)

        self.refreshoption = QLineEdit(self)
        self.refreshoption.setText(str(mySettings.refresh_setting()))
        self.refreshoption.setValidator(QIntValidator())
        self.refreshoption.setMaxLength(2)
        self.refreshoption.textChanged.connect(self.refreshtextchanged)
        flo.addRow("Refresh minutes", self.refreshoption)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        flo.addRow(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setLayout(flo)


    def accept(self):
        # print('save pressed')  # <--------------------------------DEBUG
        mySettings.pickledict['green'] = mySettings.greentemp
        mySettings.pickledict['purple'] = mySettings.purpletemp
        mySettings.pickledict['red'] = mySettings.redtemp
        mySettings.pickledict['yellow'] = mySettings.yellowtemp
        mySettings.pickledict['grey'] = mySettings.greytemp
        mySettings.pickledict['refresh'] = mySettings.refreshtemp
        mySettings.write_pickle_data()
        self.close()

    def greentextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.greentemp = string_to_list(_text)

    def purpletextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.purpletemp = string_to_list(_text)

    def redtextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.redtemp = string_to_list(_text)

    def yellowtextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.yellowtemp = string_to_list(_text)

    def greytextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.greytemp = string_to_list(_text)

    def refreshtextchanged(self, _text):
        # print(_text)  # <--------------------------------DEBUG
        mySettings.refreshtemp = abs(int(_text))


class mySystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):

        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)

        toolbaraction = self.menu.addAction(QIcon('stuff/edit.png'), "Toggle Toolbar")
        toolbaraction.triggered.connect(myGUI.show_hide_toolbar)

        scrollbaraction = self.menu.addAction(QIcon('stuff/edit.png'), "Toggle Scrollbars")
        scrollbaraction.triggered.connect(myGUI.show_hide_scrollbars)

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
    def run_loop(self):  # A slot takes no params

        refreshtime = 60 * mySettings.refresh_setting()  # seconds
        subscribe_tor = myData.return_subscriptions()

        getlist = myData.get_xml(myData.return_url_list())

        t0 = 0.0

        recentlist = []
        for initial in getlist:
            recentlist.append(initial)
            self.feedready.emit(initial)

        self.statusupdate.emit()
        self.addclock.emit(time_string())

        while True:
            # print('>>>IGNORING:', myData.return_dont_highlight_list())  #<---------------------DEBUG
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
            if t1 - t0 > 60 * 10:  # seconds
                self.addclock.emit(time_string())
                t0 = time.time()



class MyDataClass:

    def __init__(self):
        self.subscribe_tor = []
        self.feed_list = []
        self.urllist = []
        self.bangfilterlist = []
        self.get_subscriptions()
        self.get_url_list()


    def get_url_list(self):
        urllist = []
        with codecs.open(urlpath, "r", 'utf-8', errors='ignore') as readurllist:
            thelines = readurllist.readlines()
        for i in thelines:
            if len(i) > 2 and i[0] != '#':
                urllist.append(i.strip())
        self.urllist = urllist
        return self.urllist


    def url_list_length(self):
        return len(self.urllist)


    def return_dont_highlight_list(self):
        return self.bangfilterlist


    def get_subscriptions(self):
        sublist = []
        self.bangfilterlist = []  # clear the list, tor.subs.txt contents may have changed
        with codecs.open(subspath, "r", 'utf-8', errors='ignore') as readtodosubs:
            thelines = readtodosubs.readlines()
        for i in thelines:
            i = i.lower()

            # do not add lines that start with hashtag '#'
            # break the loop
            if i.strip().startswith('#'):
                continue

            # add lines with bang '!' to self.bangfilterlist
            # and then break the loop, we do not add these to subscriptions
            if i.strip().startswith('!'):
                self.bangfilterlist.append(i.strip()[1:])
                continue

            # subscribed
            i = i.strip()
            if i != '':
                sublist.append(i)

        self.subscribe_tor = sublist
        return self.subscribe_tor


    def get_xml(self, _alist):
        def looping(_url):
            counter = 0
            d = feedparser.parse(_url)

            while True:

                try:
                    publishedentry = d.entries[counter].published
                except AttributeError:
                    publishedentry = None
                except IndexError:
                    break

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

                if link is not None and 'magnet:?' in link:
                    magnet = link

                try:
                    self.feed_list.append((publishedentry, d.feed.title, d.entries[counter].title, link, magnet))
                except IndexError:  # check until end of feed
                    break
                except AttributeError:
                    logger.exception('get_xml exception AttributeError at ' + _url)
                    break  # also abort the feed if errors ################################################
                else:
                    counter += 1

        pool = ThreadPool(myData.url_list_length())
        pool.map(looping, _alist)
        pool.close()
        pool.join()

        self.feed_list = self.feed_list[::-1]
        return self.feed_list


    def return_subscriptions(self):
        return self.subscribe_tor


    def return_url_list(self):
        return self.urllist



class MyMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.opacitynumber = mySettings.opacity_setting()
        self.setWindowOpacity(self.opacitynumber)
        self.deffontsize = mySettings.font_setting()
        self.autoscroll = True
        self.auto_open_magnets = True
        self.buttonbuffer = None
        self.myclipboard = QApplication.clipboard()
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

        # hide scrollbars as default:
        self.mylistwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mylistwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.mylistwidget.itemClicked.connect(self.list_item_clicked)
        self.mylistwidget.currentItemChanged.connect(self.list_item_selected)
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
                                                        background-color: #fff;
                                                        color: #000000;
                                                        }
                                            QListWidget::item:selected:!active {
                                                        background-color: #aaa;
                                                        }
                                                            """)

        plusaction = QAction(QIcon('stuff/plus.png'), 'Larger Font\nCtrl [=]', self)
        plusaction.triggered.connect(self.plus_action)

        minusaction = QAction(QIcon('stuff/minus.png'), 'Smaller Font\nCtrl [-]', self)
        minusaction.triggered.connect(self.minus_action)

        editaction = QAction(QIcon('stuff/edit.png'), 'Edit Subscriptions\nCtrl [E]', self)
        editaction.setShortcut('Ctrl+e')
        editaction.triggered.connect(self.edit_action)

        linkaction = QAction(QIcon('stuff/link.png'), 'Edit RSS URLs\nCtrl [U]', self)
        linkaction.setShortcut('Ctrl+u')
        linkaction.triggered.connect(self.link_action)

        gearaction = QAction(QIcon('stuff/gear.png'), 'Edit RSS URLs', self)
        gearaction.triggered.connect(self.gear_action)

        fontactionplus = QAction(self)
        fontactionplus.setShortcut('Ctrl+=')
        fontactionplus.triggered.connect(self.plus_action)
        self.mylistwidget.addAction(fontactionplus)

        fontactionminus = QAction(self)
        fontactionminus.setShortcut('Ctrl+-')
        fontactionminus.triggered.connect(self.minus_action)
        self.mylistwidget.addAction(fontactionminus)

        opacityactionminus = QAction(self)
        opacityactionminus.setShortcut('Ctrl+Shift+-')
        opacityactionminus.triggered.connect(self.set_main_window_opacity_minus)
        self.mylistwidget.addAction(opacityactionminus)

        opacityactionplus = QAction(self)
        opacityactionplus.setShortcut('Ctrl+Shift+=')
        opacityactionplus.triggered.connect(self.set_main_window_opacity_plus)
        self.mylistwidget.addAction(opacityactionplus)

        scrollaction = QCheckBox('AutoScroll', self)
        scrollaction.toggle()
        scrollaction.setShortcut('Ctrl+s')
        scrollaction.stateChanged.connect(self.scroll_action_toggle)

        magnetaction = QCheckBox('Mags', self)
        magnetaction.toggle()
        magnetaction.stateChanged.connect(self.magnet_action_toggle)

        infoaction = QAction(QIcon('stuff/info.png'), 'About', self)
        infoaction.triggered.connect(self.info_action)

        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Type to filter entries")
        self.textbox.setFrame(False)
        self.textbox.textChanged.connect(self.textchanged)

        clearaction = QAction(QIcon('stuff/x.png'), 'Clear Text', self)
        clearaction.setShortcut('Esc')
        clearaction.triggered.connect(self.clear_text_field)

        self.toolbar = self.addToolBar('Toolbar Toggle')
        self.spacer = QWidget()
        self.toolbar.addAction(plusaction)
        self.toolbar.addAction(minusaction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(editaction)
        self.toolbar.addAction(linkaction)
        self.toolbar.addAction(gearaction)

        self.toolbar.addWidget(self.textbox)
        self.toolbar.addAction(clearaction)


        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(self.spacer)

        self.toolbar.addWidget(magnetaction)
        self.toolbar.addWidget(scrollaction)
        self.toolbar.addAction(infoaction)

        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))
        self.resize(1180, 500)
        self.setWindowTitle(title + ' v' + str(version))
        self.setWindowIcon(QIcon('stuff/tor.png'))
        self.setCentralWidget(self.mylistwidget)
        self.show()


    def show_hide_toolbar(self):
        self.toolbar.toggleViewAction().trigger()


    def show_hide_scrollbars(self):
        if self.mylistwidget.verticalScrollBar().isVisible() or self.mylistwidget.horizontalScrollBar().isVisible():
            self.mylistwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.mylistwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.mylistwidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.mylistwidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)


    def set_main_window_opacity_minus(self):
        self.opacitynumber -= 0.1
        if self.opacitynumber < 0.3:
            self.opacitynumber = 0.3
        self.setWindowOpacity(self.opacitynumber)
        mySettings.pickledict['opacity'] = self.opacitynumber
        mySettings.write_pickle_data()


    def set_main_window_opacity_plus(self):
        self.opacitynumber += 0.1
        if self.opacitynumber > 1.0:
            self.opacitynumber = 1.0
        self.setWindowOpacity(self.opacitynumber)
        mySettings.pickledict['opacity'] = self.opacitynumber
        mySettings.write_pickle_data()


    def change_title(self):
        self.setWindowTitle(title + ' v' + str(version) + ' @ ' + time.strftime("%X") + ' (Updated every ' + str(mySettings.refresh_setting()) + ' minutes)')


    def list_item_clicked(self, item):
        if len(item.text()) > 10:
            if item.data(201) is not None and self.auto_open_magnets:
                webbrowser.open(item.data(201))
            else:
                webbrowser.open(item.data(200))


    def list_item_selected(self, item):
        if len(item.text()) > 10:
            self.buttonbuffer = item.data(201)
            if self.buttonbuffer is not None:
                self.myclipboard.setText(self.buttonbuffer)


    def populate_me(self, _feed):

        if _feed[4] is not None:
            if _feed[3] == _feed[4]:
                magprefix = '** '
            else:
                magprefix = '* '
        else:
            magprefix = ''

        i = QListWidgetItem(magprefix + _feed[2] + '   (' + _feed[1] + ')')
        i.setData(200, _feed[3])  # url
        i.setData(201, _feed[4])  # magnet

        # HD
        if "720" in _feed[2] or "1080" in _feed[2]:
            boldHD = 55
        else:
            boldHD = 0

        i.setForeground(QColor(200 + boldHD, 200 + boldHD, 200 + boldHD))

        # red
        if any(x in str.lower(_feed[1]) for x in mySettings.red_tor()):
            i.setForeground(QColor(200 + boldHD, 0, 0))

        # gray
        if any(y in str.lower(_feed[1]) for y in mySettings.grey_tor()):
            i.setForeground(QColor(150 + boldHD, 150 + boldHD, 150 + boldHD))

        # green
        # green for inside string search, not on feed title!
        if any(y in str.lower(_feed[2]) for y in mySettings.green_tor()):
            i.setForeground(QColor(0, 200 + boldHD, 0))

        # purple
        # purple for inside string search, not on feed title!
        if any(y in str.lower(_feed[2]) for y in mySettings.purple_tor()):
            # i.setForeground(QColor(200 + boldHD, 0, 200 + boldHD))  # <--- bold capable alternative
            i.setForeground(QColor(250, 0, 250))

        # yellow
        if any(y in str.lower(_feed[1]) for y in mySettings.yellow_tor()):
            i.setForeground(QColor(150, 100, 0))

        # subscribed
        # sanitizedfeed: replace hyphens and periods so it can highlight properly
        sanitizedfeed = _feed[2].replace("-", " ").replace(".", " ")
        if any(z in str.lower(sanitizedfeed) for z in myData.return_subscriptions()):
            # omit anything starting with a bang (in myData.bangfilterlist)
            if any(z in str.lower(sanitizedfeed) for z in myData.return_dont_highlight_list()):
                pass
            else:
                i.setBackground(QColor(0, 0, 250))

        self.mylistwidget.addItem(i)
        # print(i.text())     # <--------------------------------DEBUG
        # print(i.data(200))  # <--------------------------------DEBUG
        # print(i.data(201))  # <--------------------------------DEBUG
        self.scroll_action()


    def textchanged(self, _text):
        itemlist = []
        for index in range(self.mylistwidget.count()):
            itemlist.append(self.mylistwidget.item(index))
        for i, arow in enumerate(itemlist):
            if _text.lower().strip() not in arow.text().lower():
                self.mylistwidget.setRowHidden(i, True)
            else:
                self.mylistwidget.setRowHidden(i, False)
        if _text == "":
            self.scroll_action()


    def clear_text_field(self):
        self.textbox.clear()


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


    def add_clock(self, _time):
        t = QListWidgetItem(_time)
        self.mylistwidget.addItem(t)
        self.scroll_action()


    def plus_action(self):
        self.deffontsize += 2
        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))
        mySettings.pickledict['fontsize'] = self.deffontsize
        mySettings.write_pickle_data()


    def minus_action(self):
        self.deffontsize -= 2
        if self.deffontsize < 9:
            self.deffontsize = 9
        self.mylistwidget.setFont(QFont('Arial', self.deffontsize))
        mySettings.pickledict['fontsize'] = self.deffontsize
        mySettings.write_pickle_data()


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


    def gear_action(self):
        self.childwindow = OptionDialog(self)
        self.childwindow.exec_()


    def info_action(self):
        QMessageBox.about(self, "About '" + title + "'",
                          """
                          <h3>Usage instructions and stuff:</h3>
                          <ul>
                              <li><b>Click</b> on a list item to open browser or magnet link.</li>
                              <li>One <b>*</b> means the feed has magnet link and info webpage.</li>
                              <li>Two <b>**</b> means the feed has <b>only</b> magnet link.</li>
                              <li><b>High Def</b> links appear brighter (720p & 1080p).</li>
                              <li>If <b>Mags</b> is selected, clicking will prioritize <b>direct magnet download</b> instead of webpage.</li>
                              <li>Right clicking copies magnet link to the clipboard.</li>
                              <li>If <b>Scroll</b> is selected, the list will auto scroll on update.</li>
                              <li>Type in the textbox to filter items in the list.</li>
                              <li>Ctrl + Shift plus or minus controls window opacity.</li>
                              <li>You can toggle visibility of the toolbar and scrollbars by right-clicking the tray icon.</li>
                              <br>
                              <li><b>Edit Subscriptions</b> to blue-highlight your favorites.</li>
                              <li><b>Edit RSS URLs</b> to set your RSS sources (one per line).</li>
                              <br>
                              <li>Use <b>gearbox button</b> to set options (separate with commas):
                                  <ul>
                                      <li>Green list items.</li>
                                      <li>Red list items.</li>
                                      <li>Yellow list items.</li>
                                      <li>Gray list items.</li>
                                      <li>Purple list items.</li>
                                      <li>Set the <b>refresh interval</b> (default = 5 minutes).</li>
                                  </ul>
                              </li>
                          </ul>
                          <h3>
                              <a href='https://github.com/crash-horror/torss-snacker'>Buy me a beer!</a> (scroll to the bottom.)
                          </h3>
                          <p>
                              <b>Disclaimer:</b> Use this software at your own risk, downloading copyrighted material is illegal.
                          </p>""")


    def add_warning(self, _text):
        w = QListWidgetItem(_text)
        w.setForeground(QColor(0, 0, 0))
        w.setBackground(QColor(255, 0, 0))
        self.mylistwidget.addItem(w)
        self.scroll_action()


    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()


def list_to_string(_alist):
    thestring = ''
    for s in _alist[:-1]:
        thestring += s + ', '
    return thestring + _alist[-1]


def string_to_list(_astring):
    thelist = _astring.lower().replace(' ', '').split(',')
    return list(filter(None, thelist))


def time_string():
    return "    " + time.strftime("%H:%M")


def uncaught_exception_handler(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(filename='_error.log', format='%(asctime)s :%(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logger.info('Starting...')
    sys.excepthook = uncaught_exception_handler

    mySettings = PickleData()
    myData = MyDataClass()

    app = QApplication(sys.argv)

    myGUI = MyMainWindow()

    trayIcon = mySystemTrayIcon(QIcon("stuff/tor.png"), myGUI)
    trayIcon.show()
    trayIcon.activated.connect(myGUI.tray_icon_clicked)

    app.aboutToQuit.connect(trayIcon.hide)
    sys.exit(app.exec_())


# todo highlight color picker
# Notes:
"""
pyinstaller -w -F --icon=stuff/tor.ico tor-snacker.pyw
"""
