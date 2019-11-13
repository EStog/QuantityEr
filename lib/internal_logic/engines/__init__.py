from lib.internal_logic.engines.github_engine import GithubEngine
from lib.utilities.enums import XEnum


class EngineType(XEnum):
    GITHUB = GithubEngine
    DEFAULT = GITHUB
