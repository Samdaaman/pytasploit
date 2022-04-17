from abc import ABC, abstractmethod
import random
import string
from threading import Thread
import traceback

class JobTypes:
    RUN_ENUM_SCRIPT = "RUN_ENUM_SCRIPT"


class JobStatus:
    CREATED = "CREATED"


class Job(ABC):
    def __init__(self, job_type: str):
        self.status = JobStatus.CREATED
        self.job_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        self.job_type = job_type
        self._log = ""

    def _cleanup(self) -> None:
        return

    def run(self):
        def do_work():
            try:
                self._run()
            except:
                description = traceback.format_exc()
                self.log(f'{"*"*20}\nError in {self.job_type} Job: \n{description}')
            finally:
                self._cleanup()

        Thread(target=do_work, daemon=True)

    def log(self, line: str):
        self._log += line
