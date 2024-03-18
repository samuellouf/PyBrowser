"""PyBrowser
v1.0
A simple Python web browser made with PyQt.
by: SamuelLouf <https://github.com/samuellouf>"""

import sys, os, colorsys, json, platform
from io import StringIO

__version__ = 1.0

file = __file__.replace('\\', '/')

os.chdir(file.replace(file.split('/')[-1], ''))

def get_os():
    if platform.system() == 'Windows' or platform.system() == 'Linux':
        return platform.system()
    elif platform.platform().startswith('macOS'):
        return 'macOS'
    else:
        return platform.system()

try:
    import requests
    hasRequest = True
except ImportError:
    import urllib.request
    hasRequest = False

from dialogs import *

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.uic import *
except ImportError:
    if get_os() == 'Windows':
        os.system('python -m ensurepip')
    else:
        os.system('python3 -m ensurepip')

    try:
        if get_os() == 'Windows':
            os.system('pip install PyQt5')
        else:
            os.system('python3 -m pip install PyQt5')
    except:
        print('You need to install pip.')
        input()
        exit()

try:
    from PyQt5.QtWebEngineWidgets import *
except ImportError:
    if get_os() == 'Windows':
        os.system('python -m ensurepip')
    else:
        os.system('python3 -m ensurepip')
    try:
        if get_os() == 'Windows':
            os.system('pip install PyQtWebEngine')
        else:
            os.system('python3 -m pip install PyQtWebEngine')
    except:
        print('You need to install pip.')
        input()
        exit()

def fetch_url(url):
    if hasRequest:
        try:
            response = requests.get(url)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except:
            return None
    else:
        try:
            response = urllib.request.urlopen(url)
            # Check if the request was successful (status code 200)
            return response.read()
        except:
            return None

def has_internet(timeout=6):
    if hasRequest:
        try:
            requests.get('https://www.google.com/', timeout=timeout)
            return True
        except:
            return False
    else:
        try:
            urllib.request.urlopen('https://www.google.com/', timeout=timeout)
            return True
        except:
            return False

class Browser(QMainWindow):
    def __init__(self, theme, profile, language, isPrivate : bool, size = 'default'):
        super().__init__()

        # Set window properties
        self.setWindowTitle('PyBrowser') # Title
        self.setWindowIcon(QIcon('icon.png')) # Icon
        
        if size == 'default':
            pass
        elif size == 'fullscreen':
            self.fullscreen_on()
        else:
            self.resize(int(size.split('x')[0]), int(size.split('x')[1]))
        
        self.nameChangable = True
        self.isPrivate = isPrivate
        self.profile = profile
        self.language = language
        
        self.emptyProfile = QWebEngineProfile()
        self.emptyProfile_cookie_jar = self.emptyProfile.cookieStore()
        self.emptyProfile_cookie_jar.deleteAllCookies()

        # Load Dialogs
        self.dialogs = Dialogs()
        self.dialogs.setLanguage(self.language)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)# Tabs are closable
        self.tabs.tabCloseRequested.connect(self.close_tab)# When the user tries to close a tab -> Close a tab
        self.tabs.currentChanged.connect(self.refreshAppTitle)# When the user changes tab -> Refresh the App's title
        self.tabs.currentChanged.connect(self.refreshURLBar)# When the user changes tab -> Refresh the url bar's text
        self.setCentralWidget(self.tabs)

        # Create initial tab
        self.add_tab()

        # Create navigation bar
        self.navbar = QToolBar()
        self.addToolBar(self.navbar)
        
        # BUTTONS

        # Back button
        self.back_btn = QAction(QIcon('gui/light_buttons/icon_previous_page.svg'), 'Back to previous page', self)
        self.back_btn.triggered.connect(self.current_browser().back)
        self.navbar.addAction(self.back_btn)

        # Forward button
        self.forward_btn = QAction(QIcon('gui/light_buttons/icon_next_page.svg'), 'Forward to next page', self)
        self.forward_btn.triggered.connect(self.current_browser().forward)
        self.navbar.addAction(self.forward_btn)

        # Reload button
        self.reload_btn = QAction(QIcon('gui/light_buttons/icon_reload.svg'), 'Reload page', self)
        self.reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(self.reload_btn)

        # Stop button
        self.stop_btn = QAction(QIcon('gui/light_buttons/icon_stop_load.svg'), 'Stop loading current page', self)
        self.stop_btn.triggered.connect(self.stop_loading_page)
        self.navbar.addAction(self.stop_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Home button
        self.home_btn = QAction(QIcon('gui/light_buttons/icon_home.svg'), 'Go to homepage', self)
        self.home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(self.home_btn)

        # Add new tab button
        self.add_tab_btn = QAction(QIcon('gui/light_buttons/icon_plus.png'), 'Create a new tab', self)
        self.add_tab_btn.triggered.connect(self.add_tab)
        self.navbar.addAction(self.add_tab_btn)
        
        # Customize PyBrowser
        self.customize_browser_btn = QToolButton(self)
        self.customize_browser_btn.setIcon(QIcon('gui/light_buttons/customize.svg'))
        self.customize_browser_btn.setPopupMode(2)

        # Create actions for the menu
        self.customize_browser_new_tab = QAction('Create a new tab', self)
        self.customize_browser_new_tab.triggered.connect(self.add_tab)
        
        self.customize_browser_new_window = QAction('Create a new window', self)
        self.customize_browser_new_window.triggered.connect(self.new_window)
        
        self.customize_browser_new_private_window = QAction('Create a new private navigation window', self)
        self.customize_browser_new_private_window.triggered.connect(self.new_private_navigation_window)
        
        self.customize_browser_zoom = QMenu('Zoom', self)
        
        self.customize_browser_zoom_in = QAction('Zoom in', self)
        self.customize_browser_zoom_in.triggered.connect(self.zoomIn)
        self.customize_browser_zoom_out = QAction('Zoom out', self)
        self.customize_browser_zoom_out.triggered.connect(self.zoomOut)
        self.customize_browser_reset_zoom = QAction('Reset zoom', self)
        self.customize_browser_reset_zoom.triggered.connect(self.resetZoom)
        
        self.customize_browser_zoom_level = QAction(str(int(self.getZoom() * 100)) + '%', self)
        
        self.customize_browser_zoom.addAction(self.customize_browser_zoom_in)
        self.customize_browser_zoom.addAction(self.customize_browser_zoom_out)
        self.customize_browser_zoom.addAction(self.customize_browser_reset_zoom)
        self.customize_browser_zoom.addSeparator()
        self.customize_browser_zoom.addAction(self.customize_browser_zoom_level)
        
        fullscreen = QAction('⛶', self)
        fullscreen.triggered.connect(self.toggleFullscreen)
        
        self.customize_browser_colors = QAction('Customize browser colors', self)
        self.customize_browser_colors.triggered.connect(self.customize_theme)
        
        self.customize_browser_settings = QAction('Settings', self)
        self.customize_browser_settings.triggered.connect(self.open_settings)
        
        self.customize_browser_help = QMenu('Help', self)
        
        self.customize_browser_help_about = QAction('About PyBrowser', self)
        self.customize_browser_help_about.triggered.connect(self.navigate_about)
        
        self.customize_browser_report_issue = QAction('Report an issue', self)
        self.customize_browser_report_issue.triggered.connect(self.notify_an_issue)
        
        self.customize_browser_help.addAction(self.customize_browser_help_about)
        self.customize_browser_help.addAction(self.customize_browser_report_issue)
        
        self.customize_browser_rename_window = QAction('Rename this window', self)
        self.customize_browser_rename_window.triggered.connect(self.rename_window)
        
        self.customize_browser_exit = QAction('Exit', self)
        self.customize_browser_exit.triggered.connect(self.close_app)

        # Create a menu and add actions to it
        menu = QMenu(self)
        if has_internet() and not self.isUpToDate():
            ret = QMessageBox.question(self, self.dialogs.getDialog('update'), self.dialogs.getDialog('ask-update'), QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                self.update()
                self.close_app()
            update = QAction(self.dialogs.getDialog('update'), self.update)
            menu.addAction(update)
            menu.addSeparator()
        
        menu.addAction(self.customize_browser_new_tab)
        menu.addAction(self.customize_browser_new_window)
        menu.addAction(self.customize_browser_new_private_window)
        menu.addSeparator()
        menu.addMenu(self.customize_browser_zoom)
        menu.addSeparator()
        menu.addAction(fullscreen)
        menu.addSeparator()
        menu.addAction(self.customize_browser_rename_window)
        if not self.isPrivate:
            menu.addAction(self.customize_browser_colors)
        
        menu.addSeparator()
        if not self.isPrivate:
            menu.addAction(self.customize_browser_settings)
        
        menu.addMenu(self.customize_browser_help)
        
        menu.addSeparator()
        menu.addAction(self.customize_browser_exit)
        
        menu.aboutToShow.connect(self.customize_browser_menu_opened)

        # Set the menu for the tool button
        self.customize_browser_btn.setMenu(menu)
        
        self.navbar.addWidget(self.customize_browser_btn)
        
        # Set the initial zoom level
        self.setZoom(1.0)
        
        # SETTINGS LOADING
        
        # Load dialogs
        self.loadDialogs()
        
        # Load theme
        self.customize_theme(theme, False)
        
        #
        self.destroyed.connect(self.on_window_closed)
        self.tabs.currentChanged.connect(self.refreshURLBar)

        if not isPrivate == True:
            file = __file__.replace('\\', '/')
            fs = file.replace(file.split('/')[-1], f'profiles/{profile}/firstStart')
            if not os.path.exists(fs):
                open(fs, 'x')
                self.navigate_whatsnew()
        
    def hideTabBar(self):
        self.tabs.tabBar().hide()
        
    def showTabBar(self):
        self.tabs.tabBar().show()
        
    def hideNavBar(self):
        self.navbar.hide()
    
    def showNavBar(self):
        self.navbar.show()
    
    def on_window_closed(self):
        if not self.isPrivate:
            pass
        
    def getLastestVersion(self):
        try:
            update = fetch_url('https://samuellouf.github.io/api/PyBrowser/update.json')
            update = json.loads(update)
            return float(update['lastest_version'])
        except:
            return None
        
    def isUpToDate(self):
        try:
            lastest_version = self.getLastestVersion()
            if float(lastest_version) <= __version__:
                return True
            elif float(lastest_version) > __version__:
                return False
            else:
                return None
        except:
            return None

    def update(self):
        import webbrowser
        url = 'https://samuellouf.github.io/PyBrowser#download?version=%s&os=%s' % (self.getLastestVersion(), get_os())
        webbrowser.open(url)
        self.close_app()
            
    def customize_browser_menu_opened(self):
        self.customize_browser_zoom_level.setText(str(int(self.getZoom() * 100)) + '%')
        
    def loadDialogs(self):
        self.back_btn.setText(self.dialogs.getDialog('navbar-back_btn'))
        self.forward_btn.setText(self.dialogs.getDialog('navbar-forward_btn'))
        self.reload_btn.setText(self.dialogs.getDialog('navbar-reload'))
        self.stop_btn.setText(self.dialogs.getDialog('navbar-stop'))
        self.home_btn.setText(self.dialogs.getDialog('navbar-homepage'))
        self.add_tab_btn.setText(self.dialogs.getDialog('navbar-new_tab'))
        self.customize_browser_new_tab.setText(self.dialogs.getDialog('customize_browser-new_tab'))
        self.customize_browser_new_window.setText(self.dialogs.getDialog('customize_browser-new_window'))
        self.customize_browser_new_private_window.setText(self.dialogs.getDialog('customize_browser-new_private_window'))
        self.customize_browser_zoom.setTitle(self.dialogs.getDialog('customize_browser-zoom'))
        self.customize_browser_zoom_in.setText(self.dialogs.getDialog('customize_browser-zoom_zoom_in'))
        self.customize_browser_zoom_out.setText(self.dialogs.getDialog('customize_browser-zoom_zoom_out'))
        self.customize_browser_reset_zoom.setText(self.dialogs.getDialog('customize_browser-reset_zoom'))
        self.customize_browser_colors.setText(self.dialogs.getDialog('customize_browser-colors'))
        self.customize_browser_help.setTitle(self.dialogs.getDialog('customize_browser-help'))
        self.customize_browser_help_about.setText(self.dialogs.getDialog('customize_browser-help_about'))
        self.customize_browser_report_issue.setText(self.dialogs.getDialog('customize_browser-report_issue'))
        self.customize_browser_settings.setText(self.dialogs.getDialog('customize_browser-settings'))
        self.customize_browser_rename_window.setText(self.dialogs.getDialog('customize_browser-rename_window'))
        self.customize_browser_exit.setText(self.dialogs.getDialog('customize_browser-exit'))
    
    def getWindowSize(self):
        x = self.size().width()
        y = self.size().height()
        return str(x) + 'x' + str(y)
    
    def getWindowPosition(self):
        x = self.pos().x()
        y = self.pos().y()
        return str(x) + 'x' + str(y)
        
    def rename_window(self):
        self.nameChangable = False
        name = QInputDialog(self)
        name.setLabelText(self.dialogs.getDialog('dialogs-change_window_title'))
        if name.exec_() == QInputDialog.Accepted:
            self.setWindowTitle(name.textValue())
        
    def fullscreen_on(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.navbar.setVisible(False)
        self.tabs.setTabBarAutoHide(True)
        self.showFullScreen()
        self.show()

    def fullscreen_off(self):
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.navbar.setVisible(True)
        self.tabs.setTabBarAutoHide(False)
        self.showNormal()
        self.show()

    def toggleFullscreen(self):
        # Toggle between fullscreen and normal mode
        if self.isFullScreen():
            self.fullscreen_off()
        else:
            self.fullscreen_on()

    def keyPressEvent(self, event):
        # Override key press event to handle the Escape key
        
        if event.key() == Qt.Key_F11:
            self.toggleFullscreen()
        elif event.key() == Qt.Key.Key_ZoomIn:
            self.zoomIn()
        elif event.key() == Qt.Key.Key_ZoomOut:
            self.zoomOut()
        elif event.key() == Qt.Key.Key_T and event.modifiers() == Qt.ControlModifier:
            self.add_tab()
        elif event.key() == Qt.Key.Key_N and event.modifiers() == Qt.ControlModifier:
            self.new_window()
        elif event.key() == Qt.Key.Key_N and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.new_private_navigation_window()
        else:
            super().keyPressEvent(event)

    def onZoomChanged(self, value):
        zoom_factor = value / 100
        self.setZoom(zoom_factor)

    def setZoom(self, factor = 1):
        # Set the zoom factor for the QWebEngineView
        self.current_browser().setZoomFactor(factor)
        self.customize_browser_zoom_level.setText(str(int(self.getZoom() * 100)) + '%')
        
    def resetZoom(self):
        self.setZoom(1)
    
    def getZoom(self):
        return self.current_browser().zoomFactor()
    
    def zoomIn(self):
        self.setZoom(self.getZoom() + 0.1)
    
    def zoomOut(self):
        self.setZoom(self.getZoom() - 0.1)
    
    def new_window(self):
        self.loadDialogs()
        saves_file = open('profiles/' + self.profile + '/' + 'saves.json')
        saves = json.loads(saves_file.read())
        self.window = Browser(saves['theme'], self.profile, self.language, False, self.getWindowSize())
        self.window.show()
    
    def new_private_navigation_window(self):
        self.window = Browser('#404040', self.profile, self.language, True, self.getWindowSize())
        self.window.show()
    
    def hex_to_rgb(self, hex_color):
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    
    def hex_to_hsl(self, hex_color):
        # Convert hex to RGB
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

        # Normalize RGB values to the range [0, 1]
        r /= 255.0
        g /= 255.0
        b /= 255.0

        # Convert RGB to HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Normalize HSL values to the range [0, 1]
        h %= 1.0

        return h, s, l
    
    def hsl_to_hex(self, h, s, l):

        # Normalize HSL values
        h %= 1.0
        s = max(0.0, min(1.0, s))
        l = max(0.0, min(1.0, l))

        # Convert HSL to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Normalize RGB values to the range [0, 255]
        r = int(round(r * 255))
        g = int(round(g * 255))
        b = int(round(b * 255))

        # Convert RGB to hex
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        return hex_color

    def calculate_brightness(self, hex_color):
        # Convert hex to RGB
        r, g, b = self.hex_to_rgb(hex_color)

        # Calculate relative luminance
        luminance = 0.2126 * (r / 255.0) + 0.7152 * (g / 255.0) + 0.0722 * (b / 255.0)

        return luminance
    
    def set_brightness(self, hex_color, brightness):
        h, s, l = self.hex_to_hsl(hex_color.replace('#', ''))
        return self.hsl_to_hex(h, s, brightness)

    def customize_theme(self, color = None, get_color_dialog=True):
        if get_color_dialog == True:
            color = QColorDialog(self)
            if color.exec_() == QColorDialog.Accepted:
                color = color.currentColor()
                color1 = color.name()
            else:
                color = None
        elif color != None:
            color1 = color
        
        if color != None:
            if color == 'default':
                self.navbar.setStyleSheet("QToolBar { }")
                    
                self.tabs.setStyleSheet("QTabWidget::pane { }"
                                        "QTabBar::tab:selected { }"
                                        "QTabBar::tab:!selected { }"
                                        "QTabBar::tab:hover { }")
                
                home_page = open('browser_pages/home/background_color.css', 'w')
                home_page.write("body{background-color: whitesmoke;}")
                home_page.close()
            else:
                color1_brightness = self.calculate_brightness(color1) * 100
                
                # Select text color
                if color1_brightness < 75:
                    text_color1 = '#ffffff'
                else:
                    text_color1 = '#000000'
                    

                if color1_brightness < 25:
                    color2 = self.set_brightness(color1, 0.3)
                    text_color2 = '#ffffff'
                elif color1_brightness < 50:
                    color2 = self.set_brightness(color1, 0.3)
                    text_color2 = '#ffffff'
                elif color1_brightness < 75:
                    color2 = self.set_brightness(color1, 0.3)
                    text_color2 = '#ffffff'
                else:
                    color2 = self.set_brightness(color1, 0.3)
                    text_color2 = '#000000'
                    
                if color1_brightness < 25:
                    self.back_btn.setIcon(QIcon('gui/dark_buttons/icon_previous_page.svg'))
                    self.forward_btn.setIcon(QIcon('gui/dark_buttons/icon_next_page.svg'))
                    self.reload_btn.setIcon(QIcon('gui/dark_buttons/icon_reload.svg'))
                    self.stop_btn.setIcon(QIcon('gui/dark_buttons/icon_stop_load.svg'))
                    self.home_btn.setIcon(QIcon('gui/dark_buttons/icon_home.svg'))
                    self.add_tab_btn.setIcon(QIcon('gui/dark_buttons/icon_plus.png'))
                    self.customize_browser_btn.setIcon(QIcon('gui/dark_buttons/customize.svg'))
                else:
                    self.back_btn.setIcon(QIcon('gui/light_buttons/icon_previous_page.svg'))
                    self.forward_btn.setIcon(QIcon('gui/light_buttons/icon_next_page.svg'))
                    self.reload_btn.setIcon(QIcon('gui/light_buttons/icon_reload.svg'))
                    self.stop_btn.setIcon(QIcon('gui/light_buttons/icon_stop_load.svg'))
                    self.home_btn.setIcon(QIcon('gui/light_buttons/icon_home.svg'))
                    self.add_tab_btn.setIcon(QIcon('gui/light_buttons/icon_plus.png'))
                    self.customize_browser_btn.setIcon(QIcon('gui/light_buttons/customize.svg'))
                
                if color != None:
                    self.navbar.setStyleSheet("QToolBar { background-color: " + color1 + "; color: " + text_color1 + ";}")
                    
                    self.tabs.setStyleSheet("QTabWidget::pane { background-color: " + color2 + "; color: " + text_color2 + ";}"
                                            "QTabBar::tab:selected { background-color: " + color1 + "; color: " + text_color1 + ";}"
                                            "QTabBar::tab:!selected { background-color: " + color2 + "; color: " + text_color2 + ";}"
                                            "QTabBar::tab:hover { background-color: " + color1 + "; color: " + text_color1 + ";}")
                elif color.isValid():
                    self.navbar.setStyleSheet("QToolBar { background-color: " + color1 + "; color: " + text_color1 + ";}")
                    
                    self.tabs.setStyleSheet("QTabWidget::pane { background-color: " + color2 + "; color: " + text_color2 + ";}"
                                            "QTabBar::tab:selected { background-color: " + color1 + "; color: " + text_color1 + ";}"
                                            "QTabBar::tab:!selected { background-color: " + color2 + "; color: " + text_color2 + ";}"
                                            "QTabBar::tab:hover { background-color: " + color1 + "; color: " + text_color1 + ";}")
                if not self.isPrivate:
                    saves_file = open('profiles/' + self.profile + '/' + 'saves.json')
                    saves = json.loads(saves_file.read())
                    saves['theme'] = color1
                    saves_file.close()
                    edited_saves_file = open('profiles/' + self.profile + '/' + 'saves.json', 'w')
                    edited_saves_file.write(json.dumps(saves))
                    edited_saves_file.close()
                
                
                home_page = open('browser_pages/home/background_color.css', 'w')
                home_page.write("body{background-color: " + color1 + ";}")
                home_page.close()
                
                if self.url_bar.text().split('://')[0] == 'pybrowser':
                    self.reload_page()
                    

    def add_tab(self, url = 'homepage'):
        browser = QWebEngineView()
        
        if self.isPrivate:
            browser.setPage(QWebEnginePage(self.emptyProfile, browser))
        
        if url == 'homepage':
            if self.isPrivate:
                browser.setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/private/index.html')))
            else:
                browser.setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/home/index.html')))
        elif (url == True) | (url == False):
            if self.isPrivate:
                browser.setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/private/index.html')))
            else:
                browser.setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/home/index.html')))
        else:
            browser.setUrl(QUrl(url))
            
        self.tabs.addTab(browser, "")
        self.tabs.setCurrentWidget(browser)

        # Update URL bar
        self.current_browser().urlChanged.connect(self.update_urlbar)
        
        # Add event listeners to change the app's title
        self.current_browser().urlChanged.connect(self.refreshAppTitle)
        self.current_browser().titleChanged.connect(self.refreshAppTitle)
        self.current_browser().urlChanged.connect(self.refreshURLBar)
        
    def open_settings(self):
        self.settings_window = SettingsApp(self.language)
        self.settings_window.show()
        
    def close_app(self):
        self.close()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close_app()
        
    def notify_an_issue(self):
        self.add_tab('https://github.com/samuellouf/PyBrowser/issues/new')

    def current_browser(self):
        return self.tabs.currentWidget()
    
    def loadHistoryButtons(self):
        if self.current_browser().history().canGoBack():
            self.back_btn.setVisible(True)
        else:
            self.back_btn.setVisible(False)
            
        if self.current_browser().history().canGoForward():
            self.forward_btn.setVisible(True)
        else:
            self.forward_btn.setVisible(False)
    
    def restoreReloadButtons(self):
        self.reload_btn.setVisible(True)
        self.stop_btn.setVisible(False)
    
    def reload_page(self):
        self.reload_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.current_browser().reload()
        self.current_browser().loadFinished.connect(self.restoreReloadButtons)
        self.loadHistoryButtons()
        
    def stop_loading_page(self):
        self.reload_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.current_browser().stop()
        self.loadHistoryButtons()

    def navigate_home(self):
        self.add_tab()
        if self.isPrivate:
            self.current_browser().setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/private/index.html')))
        else:
            self.current_browser().setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/home/index.html')))
        self.loadHistoryButtons()
    
    def navigate_whatsnew(self):
        self.add_tab()
        self.current_browser().setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/whats-new/index.html')))
        self.loadHistoryButtons()

    def navigate_about(self):
        self.add_tab()
        self.current_browser().setUrl(QUrl((os.getcwd().replace('\\', '/') + '/browser_pages/about/index.html')))
        self.loadHistoryButtons()

    def redirect_console(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def get_output(self):
        output = sys.stdout.getvalue()
        error = sys.stderr.getvalue()
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        return output + error
    
    def refreshURLBar(self):
        url = self.current_browser().url().toString()

        try:
            self.url_bar.setText(url)
        except:
            return

        browser_pages = os.getcwd().replace('\\', '/') + '/browser_pages/'

        if browser_pages.lower() in url.lower():
            self.url_bar.setText('pybrowser://' + url.lower().split(browser_pages.lower())[1].split('index.html')[0])
        else:
            self.url_bar.setText(url)
        
        
    def refreshAppTitle(self):
        if self.nameChangable:
            self.setWindowTitle(self.current_browser().page().title() + " | PyBrowser")
            
        try:
            if ({'name': 'index.html', 'url': 'pybrowser://home/'} == {"name": self.current_browser().page().title(), "url": self.url_bar.text()}):
                self.tabs.setTabText(self.tabs.indexOf(self.current_browser()), self.dialogs.getDialog('new_tab'))
            else:
                self.tabs.setTabText(self.tabs.indexOf(self.current_browser()), self.current_browser().page().title())
        except:
            self.tabs.setTabText(self.tabs.indexOf(self.current_browser()), self.current_browser().page().title())
        
    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        
        if q.scheme() == "":
            if "." in self.url_bar.text():
                q.setScheme("http")
            else:
                q = QUrl("https://www.google.com/search?q=" + self.url_bar.text())
        elif q.scheme() == 'pybrowser':
            if self.url_bar.text().replace('pybrowser://', '')[len(self.url_bar.text().replace('pybrowser://', '')) - 1] == '/':
                slash = ''
            else:
                slash = '/'
                
            q = QUrl(os.getcwd().replace('\\', '/') + '/browser_pages/' + self.url_bar.text().replace('pybrowser://', '') + slash + 'index.html')
            
        if not self.isPrivate:
            pass
                
        self.current_browser().setUrl(q)
        self.loadHistoryButtons()
        

    def update_urlbar(self, q):
        browser_pages_dir = os.getcwd().replace('\\', '/') + '/browser_pages/'
        if browser_pages_dir in q.toString():
            self.url_bar.setText('pybrowser://' + q.toString().split(browser_pages_dir)[1].replace('index.html', ''))
        else:
            self.url_bar.setText(q.toString())
        
        self.url_bar.setCursorPosition(0)
        self.loadHistoryButtons()

class SettingsApp(QMainWindow):
    def __init__(self, language):
        super().__init__()
        loadUi('settings/' + language + '.ui', self)  # Load the UI file

        self.dialogs = Dialogs()
        self.dialogs.setLanguage(language)

        # Set window properties
        self.setWindowTitle('PyBrowser - ' + self.dialogs.getDialog('customize_browser-settings')) # Title
        self.setWindowIcon(QIcon('icon.png')) # Icon
        
        # Connect signals and slots
        self.pushButton.clicked.connect(self.reset_color_theme)
        
        self.pushButton_6.clicked.connect(self.ok_button_clicked)
        self.pushButton_7.clicked.connect(self.cancel_button_clicked)
        self.pushButton_8.clicked.connect(self.apply_button_clicked)


    def getLang(self, string : str):
        return (string[0] + string[1]).lower()
    
    def reset_color_theme(self):
        profile = 'default'
        saves_file = open('profiles/' + profile + '/' + 'saves.json', 'r')
        saves = json.loads(saves_file.read())
        saves['theme'] = 'default'
        saves_file.close()
        saves_file = open('profiles/' + profile + '/' + 'saves.json', 'w')
        saves_file.write(json.dumps(saves))
        saves_file.close()
        
    def ok_button_clicked(self):
        self.apply_button_clicked()
        self.close()

    def cancel_button_clicked(self):
        self.close()

    def apply_button_clicked(self):
        profile = 'default'
        saves_file = open('profiles/' + profile + '/' + 'saves.json', 'r')
        saves = json.loads(saves_file.read())
        saves['language'] = self.getLang(self.comboBox.currentText())
        saves_file.close()
        saves_file = open('profiles/' + profile + '/' + 'saves.json', 'w')
        saves_file.write(json.dumps(saves))
        saves_file.close()

app = QApplication(sys.argv)
QApplication.setApplicationName("PyBrowser")

profile = 'default'
saves_file = open('profiles/' + profile + '/' + 'saves.json')
saves = json.loads(saves_file.read())

window = Browser(saves['theme'], profile, saves['language'], False)
window.show()

app.exec_()