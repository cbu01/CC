import sys
import time
import PowHelper
import PowUdp


class PowServer:
    def __init__(self, reflection_ip, reflection_port):
        self.reflection_ip = reflection_ip
        self.reflection_port = reflection_port

    def _register_server(self):
        """ Registers the server as a udp client. Returns the udp connection """
        return PowUdp.udp_send(self.reflection_ip , self.reflection_port, PowHelper.CMD_REGISTER_SERVER)

    def _send_task_to_worker(self, s, n):
        """ Sends a hashing task to worker. Returns if task sending was successful """
        return PowUdp.udp_send(self.reflection_ip , self.reflection_port, PowHelper.CMD_SEND_TASK_TO_WORKER, (s,n))

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
        try:
            udp_connection_successful = self._register_server()
            while udp_connection_successful is None:
                print "Unable to connect to reflection server. Retrying ..."
                time.sleep(5)
                udp_connection_successful = self._register_server()
        except Exception as ex:
            print "Failed to connect with reflection server. Reason is " + ex.message
            sys.exit()

        print "Udp connection established !"
        while True:
            print "Trying to send task to worker ..."
            s = PowHelper.generate_random_bit_string(128)
            task_sending_done = False

            while not task_sending_done:
                task_sending_done = self._send_task_to_worker(s, n)

            print format("Succesfully sent a task to worker. Now I wait for a reply from the worker ...")

            # Wait for reply from udp server
            while True:
                command, data = PowUdp.udp_receive(self.reflection_ip, self.reflection_port)
                if command == PowHelper.CMD_RECEIVE_WORK_FROM_WORKER:
                    s, x, n = data
                    worker_response_checks_out = self._check_worker_response(s, n, x)
                    PowUdp.udp_send(self.reflection_ip, self.reflection_port, PowHelper.CMD_TASK_SUCCESS_REPLY, worker_response_checks_out)
                    break
