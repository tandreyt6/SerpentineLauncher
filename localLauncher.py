from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

class SingleInstance(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, key: str, msg: str="raise\n"):
        super().__init__()
        self.key = key
        self._is_running = False
        self.server = None

        socket = QLocalSocket()
        socket.connectToServer(self.key)
        if socket.waitForConnected(100):
            self._is_running = True
            socket.write(bytes(msg, "utf-8"))
            socket.flush()
            socket.waitForBytesWritten(100)
            socket.disconnectFromServer()
        else:
            try:
                QLocalServer.removeServer(self.key)
            except Exception:
                pass
            self.server = QLocalServer(self)
            self.server.listen(self.key)
            self.server.newConnection.connect(self._on_new_connection)

    def is_running(self) -> bool:
        return self._is_running

    def _on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self._read_message(socket))

    def _read_message(self, socket: QLocalSocket):
        message = bytes(socket.readAll()).decode().strip()
        self.message_received.emit(message)
        socket.disconnectFromServer()
