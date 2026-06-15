"""
browser.py — A modern Python web browser built with PyQt6 + QtWebEngine (Chromium).

Run with:
    python3 browser.py
"""

import sys
import os
from PyQt6.QtCore import QUrl, Qt, QSize, QStandardPaths
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLineEdit, QPushButton,
    QStatusBar, QTabWidget, QProgressBar, QToolBar, QSizePolicy,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineProfile, QWebEngineDownloadRequest
)




# ─────────────────────────────────────────────
#  Download item widget
# ─────────────────────────────────────────────
class DownloadItemWidget(QWidget):
    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)
        self._download = download
        self._done = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        info = QVBoxLayout()
        self.lbl_name = QLabel(os.path.basename(download.downloadFileName()))
        self.lbl_name.setStyleSheet("color:#e0e2e8; font-size:12px; font-weight:600;")
        self.lbl_status = QLabel("Starting…")
        self.lbl_status.setStyleSheet("color:#6b7280; font-size:11px;")
        info.addWidget(self.lbl_name)
        info.addWidget(self.lbl_status)

        self.bar = QProgressBar()
        self.bar.setFixedHeight(6)
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        info.addWidget(self.bar)
        layout.addLayout(info, 1)

        self.btn_cancel = QPushButton("✕")
        self.btn_cancel.setFixedSize(28, 28)
        self.btn_cancel.setToolTip("Cancel")
        self.btn_cancel.clicked.connect(self._cancel)
        layout.addWidget(self.btn_cancel)

        download.receivedBytesChanged.connect(self._update_progress)
        download.isFinishedChanged.connect(self._on_finished)

    def _update_progress(self):
        dl = self._download
        received = dl.receivedBytes()
        total = dl.totalBytes()
        if total > 0:
            pct = int(received * 100 / total)
            self.bar.setValue(pct)
            self.lbl_status.setText(
                f"{self._fmt(received)} / {self._fmt(total)} — {pct}%"
            )
        else:
            self.bar.setRange(0, 0)  # indeterminate
            self.lbl_status.setText(f"{self._fmt(received)} downloaded")

    def _on_finished(self):
        self._done = True
        self.bar.setRange(0, 100)
        state = self._download.state()
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.bar.setValue(100)
            self.lbl_status.setText(f"Saved to {self._download.downloadDirectory()}")
            self.btn_cancel.setText("✓")
            self.btn_cancel.setEnabled(False)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.lbl_status.setText("Cancelled")
            self.btn_cancel.setEnabled(False)
        else:
            self.lbl_status.setText("Failed")
            self.btn_cancel.setEnabled(False)

    def _cancel(self):
        if not self._done:
            self._download.cancel()

    @staticmethod
    def _fmt(b: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"


# ─────────────────────────────────────────────
#  Download Manager Dialog
# ─────────────────────────────────────────────
class DownloadManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.resize(500, 400)
        self.setStyleSheet("""
            QDialog { background: #1a1b1e; }
            QLabel  { color: #e0e2e8; }
            QPushButton {
                background: #2d2f36; color: #c8ccd4;
                border: none; border-radius: 6px;
                font-size: 13px; font-weight: bold; padding: 4px;
            }
            QPushButton:hover  { background: #3a3d47; color:#fff; }
            QPushButton:disabled { color: #444; }
            QScrollArea, QWidget#scroll_contents {
                background: #1a1b1e; border: none;
            }
            QProgressBar {
                background: #2d2f36; border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #4a7fff, stop:1 #7c4fff);
                border-radius: 3px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        hdr = QLabel("Downloads")
        hdr.setStyleSheet("font-size:16px; font-weight:700; color:#e0e2e8; margin-bottom:8px;")
        root.addWidget(hdr)

        self._list_layout = QVBoxLayout()
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        container = QWidget()
        container.setLayout(self._list_layout)

        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #1a1b1e; }")
        root.addWidget(scroll)

        self._empty_lbl = QLabel("No downloads yet.")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet("color:#6b7280; font-size:13px;")
        self._list_layout.insertWidget(0, self._empty_lbl)

    def add_download(self, download: QWebEngineDownloadRequest):
        self._empty_lbl.hide()
        item = DownloadItemWidget(download)
        item.setStyleSheet("background:#252629; border-radius:8px;")
        # Insert before the stretch
        self._list_layout.insertWidget(self._list_layout.count() - 1, item)


class BrowserTab(QWebEngineView):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.setPage(QWebEnginePage(profile, self))

    def createWindow(self, _type):
        main = self.window()
        if isinstance(main, BrowserWindow):
            return main.add_tab()
        return super().createWindow(_type)


class BrowserWindow(QMainWindow):
    HOME = "https://eazyos.github.io/contact"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyBrowser")
        self.resize(1280, 820)

        self._profile = QWebEngineProfile("PyBrowser", self)
        self._profile.setHttpUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        # Download manager
        self._dl_dialog = DownloadManagerDialog(self)
        self._profile.downloadRequested.connect(self._on_download_requested)

        self._build_ui()
        self._apply_theme()
        self._setup_shortcuts()
        self.add_tab(self.HOME)

    def _build_ui(self):
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setContentsMargins(6, 4, 6, 4)
        self.addToolBar(toolbar)

        def nav_btn(text, tip, slot):
            btn = QPushButton(text)
            btn.setToolTip(tip)
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            return btn

        self.btn_back   = nav_btn("◀", "Go Back",    self._go_back)
        self.btn_fwd    = nav_btn("▶", "Go Forward", self._go_forward)
        self.btn_reload = nav_btn("↻", "Reload",     self._reload)
        self.btn_home   = nav_btn("⌂", "Home",       self._go_home)
        self.btn_newtab = nav_btn("+", "New Tab",    lambda: self.add_tab(self.HOME))
        self.btn_dl     = nav_btn("⬇", "Downloads",  self._show_downloads)

        for btn in [self.btn_back, self.btn_fwd, self.btn_reload, self.btn_home]:
            toolbar.addWidget(btn)

        spacer = QWidget(); spacer.setFixedWidth(6)
        toolbar.addWidget(spacer)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address…")
        self.url_bar.setMinimumHeight(32)
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.returnPressed.connect(self._navigate_to_url)
        toolbar.addWidget(self.url_bar)

        spacer2 = QWidget(); spacer2.setFixedWidth(6)
        toolbar.addWidget(spacer2)
        toolbar.addWidget(self.btn_newtab)
        toolbar.addWidget(self.btn_dl)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._progress = QProgressBar()
        self._progress.setMaximumWidth(160)
        self._progress.setMaximumHeight(14)
        self._progress.setTextVisible(False)
        self._progress.hide()
        self.status.addPermanentWidget(self._progress)

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #1a1b1e; }
            QToolBar {
                background: #1a1b1e;
                border-bottom: 1px solid #2d2f36;
                spacing: 2px;
                padding: 4px 8px;
            }
            QPushButton {
                background: #2d2f36; color: #c8ccd4;
                border: none; border-radius: 6px;
                font-size: 15px; font-weight: bold;
            }
            QPushButton:hover  { background: #3a3d47; color: #ffffff; }
            QPushButton:pressed { background: #4a4f5e; }
            QLineEdit {
                background: #252629; color: #e0e2e8;
                border: 1.5px solid #3a3d47; border-radius: 8px;
                padding: 0 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #4a7fff; }
            QTabWidget::pane { border: none; background: #141416; }
            QTabBar { background: #1a1b1e; }
            QTabBar::tab {
                background: #252629; color: #8a8f9e;
                border: none; border-radius: 6px 6px 0 0;
                padding: 6px 16px; margin-right: 2px;
                min-width: 120px; max-width: 200px; font-size: 12px;
            }
            QTabBar::tab:selected { background: #2d2f36; color: #e0e2e8; }
            QTabBar::tab:hover    { background: #2a2c33; color: #c8ccd4; }
            QStatusBar {
                background: #1a1b1e; color: #6b7280;
                font-size: 11px; border-top: 1px solid #2d2f36;
            }
            QProgressBar {
                background: #2d2f36; border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #4a7fff, stop:1 #7c4fff);
                border-radius: 3px;
            }
        """)

    def _setup_shortcuts(self):
        from PyQt6.QtGui import QShortcut
        QShortcut(QKeySequence("Ctrl+T"),    self, lambda: self.add_tab(self.HOME))
        QShortcut(QKeySequence("Ctrl+W"),    self, self._close_current_tab)
        QShortcut(QKeySequence("Ctrl+R"),    self, self._reload)
        QShortcut(QKeySequence("F5"),        self, self._reload)
        QShortcut(QKeySequence("Ctrl+L"),    self, self._focus_url_bar)
        QShortcut(QKeySequence("Alt+Left"),  self, self._go_back)
        QShortcut(QKeySequence("Alt+Right"), self, self._go_forward)
        QShortcut(QKeySequence("Ctrl+Tab"),  self, self._next_tab)
        QShortcut(QKeySequence("Ctrl+J"),    self, self._show_downloads)

    def add_tab(self, url=HOME):
        view = BrowserTab(self._profile, self)
        idx = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(idx)
        view.setUrl(QUrl(url))
        view.titleChanged.connect(lambda t, v=view: self._update_tab_title(v, t))
        view.urlChanged.connect(lambda u, v=view: self._on_url_changed(v, u))
        view.loadProgress.connect(self._on_load_progress)
        view.loadFinished.connect(self._on_load_finished)
        view.loadStarted.connect(self._on_load_started)
        view.iconChanged.connect(lambda ic, v=view: self._update_tab_icon(v, ic))
        return view

    def _close_tab(self, idx):
        if self.tabs.count() == 1:
            self.close(); return
        w = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        if w: w.deleteLater()

    def _close_current_tab(self):
        self._close_tab(self.tabs.currentIndex())

    @property
    def _current_view(self):
        return self.tabs.currentWidget()

    def _navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text: return
        if "." in text and " " not in text and not text.startswith("http"):
            text = "https://" + text
        elif not text.startswith(("http://", "https://", "file://", "about:")):
            text = f"https://www.google.com/search?q={text.replace(' ', '+')}"
        if v := self._current_view:
            v.setUrl(QUrl(text))

    def _go_back(self):
        if v := self._current_view: v.back()
    def _go_forward(self):
        if v := self._current_view: v.forward()
    def _reload(self):
        if v := self._current_view: v.reload()
    def _go_home(self):
        if v := self._current_view: v.setUrl(QUrl(self.HOME))
    def _focus_url_bar(self):
        self.url_bar.setFocus(); self.url_bar.selectAll()
    def _next_tab(self):
        n = self.tabs.count()
        self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % n)

    def _on_tab_changed(self, idx):
        view = self.tabs.widget(idx)
        if isinstance(view, BrowserTab):
            self.url_bar.setText(view.url().toString())
            self.setWindowTitle(view.title() or "PyBrowser")
            self._update_nav_buttons(view)

    def _on_url_changed(self, view, url):
        if view is self._current_view:
            self.url_bar.setText(url.toString())
        self._update_nav_buttons(view)

    def _on_load_started(self):
        self._progress.show(); self._progress.setValue(0)
        self.btn_reload.setText("✕")
        self.status.showMessage("Loading…")

    def _on_load_progress(self, p):
        self._progress.setValue(p)

    def _on_load_finished(self, ok):
        self._progress.hide(); self.btn_reload.setText("↻")
        self.status.showMessage("Done" if ok else "Load failed", 2000)

    def _update_tab_title(self, view, title):
        idx = self.tabs.indexOf(view)
        if idx >= 0:
            self.tabs.setTabText(idx, (title[:22] + "…") if len(title) > 24 else title or "New Tab")
        if view is self._current_view:
            self.setWindowTitle(title or "PyBrowser")

    def _update_tab_icon(self, view, icon):
        idx = self.tabs.indexOf(view)
        if idx >= 0: self.tabs.setTabIcon(idx, icon)

    def _show_downloads(self):
        self._dl_dialog.show()
        self._dl_dialog.raise_()

    def _on_download_requested(self, download: QWebEngineDownloadRequest):
        # Ask user where to save
        default_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        suggested = os.path.join(default_dir, download.downloadFileName())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", suggested
        )
        if not path:
            download.cancel()
            return

        download.setDownloadDirectory(os.path.dirname(path))
        download.setDownloadFileName(os.path.basename(path))
        download.accept()

        self._dl_dialog.add_download(download)
        self._dl_dialog.show()
        self._dl_dialog.raise_()
        self.status.showMessage(f"Downloading: {os.path.basename(path)}", 3000)

    def _update_nav_buttons(self, view):
        self.btn_back.setEnabled(view.history().canGoBack())
        self.btn_fwd.setEnabled(view.history().canGoForward())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyBrowser")
    app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()