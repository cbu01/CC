from PowServer import PowServer

reflection_ip = "100.100.100.100"
reflection_port = 12345
n = 20

server = PowServer(reflection_ip, reflection_port)
server.run(n)