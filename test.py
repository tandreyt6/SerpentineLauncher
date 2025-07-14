import socket

def is_connected(host="8.8.8.8", port=53, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False

# Пример использования
if is_connected():
    print("Интернет есть")
else:
    print("Нет подключения")
