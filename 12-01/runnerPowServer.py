from PowServer import PowServer

own_port = 10001
client_ip = "10.2.16.168"
client_port = 10000
n = 20

server = PowServer(own_port, client_ip, client_port)
server.run(n)
