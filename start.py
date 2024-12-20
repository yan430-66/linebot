from server import Server
from src.color import C, W
from webui import webui
import argparse
class start(Server, webui):
    def __init__(self,
                 config_path: str = './cfg.yaml',
                 debug=False,
                 server_log: str | bool= None):
       
        if debug: 
            print(f"{C['cyan']}Running in debug mode...{W}",)
            webui.__init__(self, config_path=config_path)
        else:
            super().__init__(config_path=config_path, server_log=server_log)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action='store_true', help='open in debug mode',)
    parser.add_argument('-cfg', type=str, help='cfg path ', default='./cfg.yaml')
    parser.add_argument('--outputlog', action='store_true', help='log file',)
    args = parser.parse_args()

    if args.debug:
        server = start(debug=args.debug, config_path=args.cfg)
        server.start_debugui()
    else:
        # Normal server start
        if args.outputlog:
            server = start(config_path=args.cfg, server_log=args.outputlog)
        else:
            server = start(config_path=args.cfg)
        
        server.run()

    
