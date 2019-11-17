from lib.classes.internal.engines.github_v3_engine import GithubV3Engine

ENGINE_TYPE = {
    GithubV3Engine.ARG_NAME: GithubV3Engine,
}

DEFAULT_ENGINE_TYPE = GithubV3Engine.ARG_NAME
