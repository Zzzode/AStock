import asyncio

import pytest

from astock.utils.cache import DataCache


@pytest.mark.asyncio
async def test_get_or_set_awaits_coroutine_value() -> None:
    cache = DataCache()

    async def factory() -> int:
        await asyncio.sleep(0)
        return 42

    value = await cache.get_or_set("daily", "key", lambda: factory())

    assert value == 42
