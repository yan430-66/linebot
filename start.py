from server import Server
from src.color import C, W
from webui import webui
import argparse
class start(Server, webui):
    def __init__(self,
                 token: str = None, 
                 secret: str = None, 
                 port: int = 8000, 
                 url: str = None, 
                 debug=False):
       
        if debug: 
            print(f"{C['cyan']}Running in debug mode...{W}",)
            webui.__init__(self, )
        else:
            super().__init__(token=token, secret=secret, port=port, url=url)

if __name__ == "__main__":
    # sys.stdout = Logger(FILE_NAME)
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action='store_true', help='open in debug mode',)
    parser.add_argument('-T', type=str, help='LINE CHANNEL ACCESS TOKEN', required=False)
    parser.add_argument('-S', type=str, help='LINE CHANNEL SECRET', required=False)
    parser.add_argument('-P', type=int, help='PORT', default=8000)
    parser.add_argument('-ngrok', type=str, help='ngrok url if opened', default=None)
    args = parser.parse_args()

    if args.debug:
        server = start(debug=True,)
        server.start_debugui()
    else:
        if not args.T or not args.S:
            raise ValueError("LINE CHANNEL ACCESS TOKEN (-T) and SECRET (-S) are required unless running in debug mode.")

        # Normal server start
        server = start(token=args.T, secret=args.S, port=args.P, url=args.ngrok,)
        server.run()

    
