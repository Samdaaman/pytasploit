from abc import ABC, abstractmethod
import subprocess
from typing import List, Optional

from my_logging import Logger

logger = Logger('SERVICE_CONN')


class CredentialConsumerServiceConnector(ABC):
    """Credential Consumers Service Connectors are models that require credentials (ie mysql)"""
    def __init__(self, name: str, is_supported=True, default_usernames: Optional[List[str]] = None):
        self.name = name
        self.is_supported = is_supported
        self.default_usernames = default_usernames if default_usernames is not None else []  # type: List[str]

    @abstractmethod
    def _test_creds(self, username: str, password: str) -> bool:
        ...

    @staticmethod
    def _test_exit_code(cmd: str, timeout: float = 5.0):
        try:
            result = subprocess.run(cmd, shell=True, timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warn("Timeout expired in CredentialConsumerServiceConnector._test_exit_code, consider refactoring test")
            return False
