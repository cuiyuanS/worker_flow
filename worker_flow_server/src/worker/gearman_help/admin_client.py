from src.lib.gearman import GearmanAdminClient


class AdminClient:

    def __init__(self, address=["127.0.0.1:4730"]):
        self.gm_client = GearmanAdminClient(address)

    # @func_set_timeout(0.5)
    def workers(self):
        return self.gm_client.get_workers()

    # @func_set_timeout(0.5)
    def workers_status(self):
        return self.gm_client.get_status()

    def get_workers(self):
        try:
            return self.workers()
        except BaseException as e:
            return []

    def get_workers_status(self):
        try:
            return self.workers_status()
        except BaseException as e:
            return []

    def try_connect(self):
        try:
            self.gm_client.establish_admin_connection()
        except Exception as e:
            return False
        return True
