import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QNetworkProxy
from PyQt5.QtWebEngineCore import *
import subprocess

startpage = "https://www.duckduckgo.com/"
directory = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
homepage = "file://" + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/pages/mainpage/index.html"
aboutpage = "file://" + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/pages/about/index.html"

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Create the QTabWidget and add it to the central widget area
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.setWindowTitle("GedWeb")
        self.setWindowIcon(QIcon("GedWeb.ico"))
        settings = QSettings('Gedon76', 'GedWeb')
        size = settings.value('Browser/Size', QSize(800, 600))
        state = settings.value('Browser/State', None)
        if state is not None:
            self.restoreState(state)
        self.resize(size)

        # Create a new tab for the default homepage
        self.add_tab(startpage)
        self.navtb = QToolBar()
        self.addToolBar(self.navtb)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        back_btn = QAction('🡄', self)
        back_btn.triggered.connect(self.current_browser().back)
        self.navtb.addAction(back_btn)

        forward_btn = QAction('🡆', self)
        forward_btn.triggered.connect(self.current_browser().forward)
        self.navtb.addAction(forward_btn)

        reload_btn = QAction('🔁', self)
        reload_btn.triggered.connect(self.current_browser().reload)
        self.navtb.addAction(reload_btn)

        home_btn = QAction('⌂', self)
        home_btn.triggered.connect(self.go_to_homepage)
        self.navtb.addAction(home_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navtb.addWidget(self.urlbar)
        daurlbar = self.urlbar

        downloads_btn = QAction('⬇', self)
        downloads_btn.triggered.connect(self.show_downloads)
        self.navtb.addAction(downloads_btn)

        other_btn = QAction('☰', self)
        other_btn.triggered.connect(self.show_other_menu)
        self.navtb.addAction(other_btn)

        addtab_btn = QToolButton()
        addtab_btn.setText('ᐩ')
        addtab_btn.clicked.connect(lambda: self.add_tab(homepage))
        self.tabs.setCornerWidget(addtab_btn, Qt.TopRightCorner)

        self.history_menu = QMenu(self)
        self.other_menu = QMenu(self)
        self.downloads_menu = QMenu(self)

        self.show()

        self.tabs.currentChanged.connect(self.update_urlbar)
        self.current_browser().loadFinished.connect(self.update_title)
        self.current_browser().loadFinished.connect(self.update_urlbar)

    def add_tab(self, url):
        # Create a new QWebEngineView and add it as a tab
        browser = QWebEngineView()

        # Connect the downloadRequested signal to the handle_download method
        browser.page().profile().downloadRequested.connect(self.handle_download)

        browser.setUrl(QUrl(url))
        browser.setWindowTitle(browser.page().title())

        index = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentWidget(browser)

        # Connect titleChanged signal to update_tab_title function
        browser.page().titleChanged.connect(lambda title: self.update_tab_title(index, title))

        # Create a close button for the tab
        close_btn = QToolButton()
        close_btn.setText('x')
        close_btn.clicked.connect(lambda: self.close_tab(index))
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, close_btn)
        self.update_title()


    def close_tab(self, index):
        # Close the tab at the given index
        widget = self.tabs.widget(index)
        if widget is not None:
            self.tabs.removeTab(index)  
        self.update_title()

    def update_tab_title(self, index, title):
        # Update tab title
        self.tabs.setTabText(index, title)

    def current_browser(self):
        # Get the QWebEngineView for the current tab
        return self.tabs.currentWidget()
    
    def go_to_homepage(self):
        url = QUrl(homepage)
        self.current_browser().setUrl(url)

    def update_title(self):
        title = self.current_browser().page().title()
        self.setWindowTitle('% s (GedWeb)' % title)
        icon_url = self.current_browser().page().iconUrl().toString()

        # Установите значок окна, используя полученный URL
        self.setWindowIcon(QIcon(icon_url))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if self.urlbar.text() == "gedweb://about":
            q = QUrl(aboutpage)
        elif self.urlbar.text() == "gedweb://home":
            q = QUrl(homepage)
        elif self.is_url_reachable(self.urlbar.text()):
            q = QUrl('http://' + self.urlbar.text())
        else:
            q = QUrl('http://duckduckgo.com/?q=% s' % self.urlbar.text().replace(' ', '+'))
        self.current_browser().setUrl(q)

    def update_urlbar(self):
        self.urlbar.setText(self.current_browser().url().toString())
        self.urlbar.setCursorPosition(0)
    def is_url_reachable(self, url):
        # Проверяем, доступен ли URL-адрес
        command = ['ping', '/n', '1', url]
        return subprocess.call(command) == 0


    def closeEvent(self, event):
        # Save the current size and state of the main window in QSettings
        settings = QSettings('Gedon76', 'GedWeb')
        settings.setValue('Browser/Size', self.size())
        settings.setValue('Browser/State', self.saveState())
        super(MainWindow, self).closeEvent(event)
        
    def show_history_menu(self):
        # Clear the history menu and add the session history
        self.history_menu.clear()
        history = self.current_browser().history()
        for i in range(history.count()):
            url = history.itemAt(i).url()
            action = QAction(url.toString(), self)
            action.triggered.connect(lambda checked, url=url: self.current_browser().setUrl(url))
            self.history_menu.addAction(action)

        # Show the history menu under the history button
        pos = self.mapToGlobal(self.navtb.pos()) + QPoint(0, self.navtb.height()) + QPoint(self.navtb.width(), 0)
        self.history_menu.popup(pos)

    def show_downloads(self):
        print("Sorry! I'm too dumb to code that :P")

    # Функция-обработчик события для пункта загрузки
    def handle_download(self, download):
        # Получение имени файла загрузки
        file_name = download.suggestedFileName()

        # Получение папки загрузок
        download_folder = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)

        # Отображение диалогового окна сохранения файла
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", 
                                                download_folder + "/" + file_name,
                                                "Все файлы (*)", options=options)

        if file_path:
            # Сохранение файла
            download.setPath(file_path)
            download.accept()


    def show_other_menu(self):
        self.other_menu.clear()
        actionNT = QAction('New Tab (Home Page)', self)
        actionNT.triggered.connect(lambda: self.add_tab(homepage))
        self.other_menu.addAction(actionNT)
        actionAB = QAction('About GedWeb', self)
        actionAB.triggered.connect(lambda: self.add_tab(aboutpage))
        self.other_menu.addAction(actionAB)
        actionHT = QAction('History', self)
        actionHT.triggered.connect(self.show_history_menu)
        self.other_menu.addAction(actionHT)

        pos = self.mapToGlobal(self.navtb.pos()) + QPoint(0, self.navtb.height()) + QPoint(self.navtb.width(), 0)
        self.other_menu.popup(pos)



if __name__ == "__main__":
    app = QApplication(['GedWeb', '--no-sandbox'])
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setApplicationName("GedWeb")
    window = MainWindow()
    window.show()  # отображаем окно
    window.update_title()  # вызываем метод после отображения окна
    sys.exit(app.exec_())
