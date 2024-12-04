from server import Server
import argparse

class start(Server):
    def __init__(self, token, secret, port):
        super().__init__(token, secret, port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-T', type=str, help='LINE CHANNEL ACCESS TOKEN', required=True)
    parser.add_argument('-S', type=str, help='LINE CHANNEL SECRET', required=True)
    parser.add_argument('-P', type=int, help='PORT', default=8000)
    parser.add_argument('-ngrok', type=str, help='ngrok url if opened', default=None)
    args = parser.parse_args()
    server = start(token=args.T, secret=args.S, port=args.P , url=args.ngrok)

    
