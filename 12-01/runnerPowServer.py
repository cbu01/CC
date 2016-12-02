from PowServer import PowServer

own_port = 10001
reflection_ip = ''
reflection_port = 10559
n = 20

server = PowServer(own_port, reflection_ip, reflection_port)
server.run(n)
