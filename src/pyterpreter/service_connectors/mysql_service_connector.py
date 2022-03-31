import shutil

from pyterpreter.service_connectors.credential_consumer_connector import CredentialConsumerServiceConnector


class CCMysql(CredentialConsumerServiceConnector):
    def __init__(self):
        super().__init__(
            "mysql",
            is_supported=shutil.which("mysql") is not None,
            default_usernames=["root", "sql", "mysql"]
        )

    def _test_creds(self, username: str, password: str) -> bool:
        return super()._test_exit_code("mysql -u'{}' -p'{}' -e''")
