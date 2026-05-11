from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider

from core.di.providers.ai import AIProvider
from core.di.providers.auth import AuthProvider
from core.di.providers.cache import CacheProvider
from core.di.providers.config import ConfigProvider
from core.di.providers.crypt import CryptProvider
from core.di.providers.db import DBProvider
from core.di.providers.repositories import RepositoriesProvider
from core.di.providers.services import ServicesProvider


def build_container():
    return make_async_container(
        ConfigProvider(),
        DBProvider(),
        CacheProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
        FastapiProvider(),
        CryptProvider(),
        AuthProvider(),
        AIProvider(),
    )
