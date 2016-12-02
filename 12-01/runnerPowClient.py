from PowClient import PowClient

own_port = 10000
server_ip = ''
server_port = 10001

server = PowClient(own_port, server_ip, server_port)
server.run()
