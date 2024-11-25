# Configuration options for the agent running in the loop
import os
import time
from typing import Union, Any, Dict, List
from .options import browser_options

class Config:
    def __init__(self) -> None:
        self.loop_duration: int = self._get_env_as_int('LOOP_DURATION', 100)
        self.scenario_name: str = os.getenv('SCENARIO_NAME', 'default_scenario')
        self.user_name: str = os.getenv('USER_NAME', 'default_user')
        self.lang: str = os.getenv('LANGUAGE', 'en-US')
        self.storage_path: str = self._setup_storage_path()
        self.log_file: str = os.getenv('LOG_FILE', os.path.join(self.storage_path, f'app_{time.time()}.log'))
        self.browser_options: List[str] = self._setup_browser_options()
        self.proxy: Union[bool, Dict] = False
        self._setup_proxy()

    def _get_env_as_int(self, env_var: str, default: int) -> int:
        return int(os.getenv(env_var, str(default)))

    def _setup_browser_options(self) -> List[str]:
        return ['--window-position=0,0', '--window-size=500,860'] + browser_options

    def _setup_storage_path(self) -> str:
        storage_path = os.getenv('STORAGE_PATH', os.path.join(self.scenario_name, self.user_name))
        os.makedirs(storage_path, exist_ok=True)
        return storage_path

    def _setup_proxy(self) -> None:
        """If PROXY_SERVER is provided setup proxy configuration"""
        server = os.getenv('PROXY_SERVER', False)
        if server:
            self.browser_options.append(f"--proxy-server={server}")
            username = os.getenv('PROXY_USERNAME', None)
            password = os.getenv('PROXY_PASSWORD', None)
            self.proxy = {
                'server': server,
                'username': username,
                'password': password
            }


    def to_dict(self) -> Dict[str, Any]:
        return {
            'loop_duration': self.loop_duration,
            'scenario_name': self.scenario_name,
            'user_name': self.user_name,
            'browser_options': self.browser_options,
            'lang': self.lang,
            'storage_path': self.storage_path,
            'log_file': self.log_file,
            'proxy': self.proxy
        }

config = Config()