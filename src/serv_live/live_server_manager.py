import os
import socket
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QThread

from .handler import LiveServerRequestHandler

class FileWatcherThread(QThread):
    """Watches a directory for file changes and emits a new token."""
    changes_detected = Signal(float)

    def __init__(self, directory: str, parent=None):
        super().__init__(parent)
        self._directory = directory
        self._running = True
        self._last_token = 0.0

    def run(self):
        while self._running:
            try:
                max_mtime = 0.0
                for root, _, files in os.walk(self._directory):
                    for name in files:
                        try:
                            mtime = os.path.getmtime(os.path.join(root, name))
                            if mtime > max_mtime:
                                max_mtime = mtime
                        except OSError:
                            continue
                
                if max_mtime > self._last_token:
                    self._last_token = max_mtime
                    self.changes_detected.emit(self._last_token)

            except Exception as e:
                print(f"[LiveServer] File watcher error: {e}")

            time.sleep(1) # Check every second

    def stop(self):
        self._running = False

class LiveServerManager(QObject):
    """Manages the lifecycle of the live server and file watcher."""
    server_started = Signal(str, int)
    server_stopped = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = None
        self._server_thread = None
        self._watcher_thread = None
        self._root_path = None
        self._change_token = time.time()

    def get_change_token(self):
        return self._change_token

    def _update_change_token(self, token: float):
        self._change_token = token

    def is_running(self):
        return self._server is not None and self._server_thread is not None and self._server_thread.is_alive()

    def start(self, root_path: str, port: int = 0, open_browser: bool = False):
        if self.is_running():
            self.error.emit("Server is already running.")
            return

        self._root_path = root_path
        
        try:
            if port == 0:
                port = self._find_free_port()
            host = '127.0.0.1'

            # Custom handler needs a way to get the change token
            handler_factory = lambda *args, **kwargs: LiveServerRequestHandler(
                *args, directory=self._root_path, change_token_provider=self.get_change_token, **kwargs
            )

            self._server = ThreadingHTTPServer((host, port), handler_factory)
            
            # Start server in a separate thread
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()

            # Start file watcher
            self._watcher_thread = FileWatcherThread(self._root_path)
            self._watcher_thread.changes_detected.connect(self._update_change_token)
            self._watcher_thread.start()

            self.server_started.emit(host, port)

            if open_browser:
                webbrowser.open(f"http://{host}:{port}")

        except Exception as e:
            self.error.emit(f"Failed to start server: {e}")
            self._cleanup()

    def _run_server(self):
        # Change CWD for the server thread so SimpleHTTPRequestHandler serves from the right place
        os.chdir(self._root_path)
        if self._server:
            self._server.serve_forever()

    def stop(self):
        if not self.is_running():
            return
        
        try:
            if self._watcher_thread:
                self._watcher_thread.stop()
                self._watcher_thread.wait()

            if self._server:
                self._server.shutdown()
                self._server.server_close()
            
            if self._server_thread:
                self._server_thread.join(timeout=2)

            self.server_stopped.emit()
        except Exception as e:
            self.error.emit(f"Error while stopping server: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        self._server = None
        self._server_thread = None
        self._watcher_thread = None
        self._root_path = None

    def _find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]