from . import WorkerAsync


class AIGenMode(WorkerAsync):
    def __init__(self, gearman_worker, gearman_job):
        super(AIGenMode, self).__init__(gearman_worker, gearman_job)
        self.worker_mark = "2DC3D_Flame_FFHQ"
