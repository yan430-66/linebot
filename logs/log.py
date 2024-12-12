import sys
from datetime import datetime
WEB_LOG = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_web.log"
SERVER_LOG = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_server.log"
# WEB_LOG = f"logs/test_web.log"
# SERVER_LOG = f"logs/test_server.log"
def log_pth():
    server_log = open(SERVER_LOG, "w", encoding="utf-8")
    server_log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Server log\n")
    server_log.close()
    return SERVER_LOG

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # Write the data of the buffer to the file
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def isatty(self):
        return False 