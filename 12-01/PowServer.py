import PowHelper
import PowUdp


class PowServer:
    def __init__(self, own_port, client_ip, client_port):
		self.own_port = own_port
        self.client_ip = client_ip
        self.client_port = client_port

    def _send_task_to_worker(self, s, n):
        """ Sends a hashing task to worker  """
        PowUdp.udp_send(self.own_port, self.client_ip , self.client_port, PowHelper.CMD_SEND_TASK_TO_WORKER, (s,n))

    def _check_worker_response(self, s, n, x):
        """ Checks the response of a worker. Returns if hashes are verified """
        print "Received response from worker"
        hash_verified = PowHelper.verify_hash(s, n, x)
        if hash_verified:
            print "Successfully verified hash calculation from worker"
        else:
            print "Hash from worker NOT verified !"

        return hash_verified

    def run(self, n):
        print "Running PowServer"

        while True:
            print "Trying to send task to worker ..."
            s = PowHelper.generate_random_bit_string(128)
            self._send_task_to_worker(s, n)

            print format("Hopefully some worker got a task. Now I wait for a reply from him ...")

            # Wait for reply from udp server
            while True:
                command, data = PowUdp.udp_receive(self.client_port)
                if command == PowHelper.CMD_RECEIVE_WORK_FROM_WORKER:
                    s, x, n = data
                    worker_response_checks_out = self._check_worker_response(s, n, x)
                    PowUdp.udp_send(self.own_port, self.client_ip, self.client_port, PowHelper.CMD_TASK_SUCCESS_REPLY, worker_response_checks_out)
                    break
