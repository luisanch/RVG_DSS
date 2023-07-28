from simple_websocket_server import WebSocketServer, WebSocket

class Server(WebSocket):
    def handle(self):
        for client in clients:
            if client != self:
                client.send_message(self.data)

    def connected(self):
        print(self.address, 'connected')
        clients.append(self)

    def handle_close(self):
        clients.remove(self)
        print(self.address, 'closed')

clients = []
server = WebSocketServer('', 8000, Server)
server.serve_forever()