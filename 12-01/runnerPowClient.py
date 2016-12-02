from PowClient import PowClient

own_port = 10000
reflection_ip = ''
reflection_port = 10559

server = PowClient(own_port, reflection_ip, reflection_port)
server.run()
