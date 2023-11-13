# -*- encoding: utf-8

from __future__ import absolute_import

import time

from .connection_manager import GearmanConnectionManager
from .admin_client_handler import GearmanAdminClientCommandHandler
from .errors import (
    ConnectionError,
    GearmanError,
    InvalidAdminClientState,
    ServerUnavailable
)
from .protocol import GEARMAN_COMMAND_ECHO_REQ, \
    GEARMAN_SERVER_COMMAND_STATUS, GEARMAN_SERVER_COMMAND_VERSION, GEARMAN_SERVER_COMMAND_WORKERS, \
    GEARMAN_SERVER_COMMAND_MAXQUEUE, GEARMAN_SERVER_COMMAND_SHUTDOWN, GEARMAN_SERVER_COMMAND_GETPID, \
    GEARMAN_SERVER_COMMAND_CANCEL_JOB, GEARMAN_SERVER_COMMAND_SHOW_JOBS, GEARMAN_SERVER_COMMAND_SHOW_UNIQUE_JOBS
from .util import unlist


ECHO_STRING = "ping? pong!"
DEFAULT_ADMIN_CLIENT_TIMEOUT = 0.5


class GearmanAdminClient(GearmanConnectionManager):
    """GearmanAdminClient :: Interface to send/receive administrative commands to a Gearman src

    This client acts as a BLOCKING client and each call will poll until it receives a satisfactory src response

    http://gearman.org/index.php?id=protocol
    See section 'Administrative Protocol'
    """
    command_handler_class = GearmanAdminClientCommandHandler

    def __init__(self, host_list=None, poll_timeout=DEFAULT_ADMIN_CLIENT_TIMEOUT):
        super(GearmanAdminClient, self).__init__(host_list=host_list)
        self.poll_timeout = poll_timeout

        # TODO: We could change the API here so this class only allows
        # passing a single host, not a list.
        try:
            self.current_connection = unlist(self.connection_list)
        except ValueError:
            raise GearmanError(
                "Only pass a single host to the constructor of %s" %
                type(self).__name__)

        self.current_handler = None

    def establish_admin_connection(self):
        try:
            self.establish_connection(self.current_connection)
        except ConnectionError:
            raise ServerUnavailable('Found no valid connections in list: %r' % self.connection_list)

        self.current_handler = self.connection_to_handler_map[self.current_connection]

    def ping_server(self):
        """Sends off a debugging string to execute an application ping on the Gearman src"""
        start_time = time.time()

        self.establish_admin_connection()
        self.current_handler.send_echo_request(ECHO_STRING)
        server_response = self.wait_until_server_responds(GEARMAN_COMMAND_ECHO_REQ)
        if server_response != ECHO_STRING:
            raise InvalidAdminClientState("Echo string mismatch: got %s, expected %s" % (server_response, ECHO_STRING))

        elapsed_time = time.time() - start_time
        return elapsed_time

    def send_maxqueue(self, task, max_size):
        """Sends a request to change the maximum queue size for a given task"""

        self.establish_admin_connection()
        self.current_handler.send_text_command('%s %s %s' % (GEARMAN_SERVER_COMMAND_MAXQUEUE, task, max_size))
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_MAXQUEUE)

    def send_shutdown(self, graceful=True):
        """Sends a request to shutdown the connected gearman src"""
        actual_command = GEARMAN_SERVER_COMMAND_SHUTDOWN
        if graceful:
            actual_command += ' graceful'

        self.establish_admin_connection()
        self.current_handler.send_text_command(actual_command)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_SHUTDOWN)

    def get_status(self):
        """Retrieves a list of all registered tasks and reports how many items/workers are in the queue"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_STATUS)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_STATUS)

    def get_version(self):
        """Retrieves the version number of the Gearman src"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_VERSION)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_VERSION)

    def get_workers(self):
        """Retrieves a list of workers and reports what tasks they're operating on"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_WORKERS)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_WORKERS)

    def wait_until_server_responds(self, expected_type):
        current_handler = self.current_handler

        def continue_while_no_response(any_activity):
            return (not current_handler.response_ready)

        self.poll_connections_until_stopped([self.current_connection], continue_while_no_response, timeout=self.poll_timeout)
        if not self.current_handler.response_ready:
            raise InvalidAdminClientState('Admin client timed out after %f second(s)' % self.poll_timeout)

        cmd_type, cmd_resp = self.current_handler.pop_response()
        if cmd_type != expected_type:
            raise InvalidAdminClientState('Received an unexpected response... got command %r, expecting command %r' % (cmd_type, expected_type))

        if type(cmd_resp) == bytes:
            return cmd_resp.decode("utf-8")
        return cmd_resp

    def get_pid(self):
        """Retrieves the process ID"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_GETPID)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_GETPID)

    def cancel_job(self, handle):
        """Cancels a job"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_CANCEL_JOB + " " + handle)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_CANCEL_JOB)

    def get_jobs(self):
        """Retrieves a list of jobs"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_SHOW_JOBS)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_SHOW_JOBS)

    def get_unique_jobs(self):
        """Retrieves a list of unique jobs"""
        self.establish_admin_connection()
        self.current_handler.send_text_command(GEARMAN_SERVER_COMMAND_SHOW_UNIQUE_JOBS)
        return self.wait_until_server_responds(GEARMAN_SERVER_COMMAND_SHOW_UNIQUE_JOBS)
