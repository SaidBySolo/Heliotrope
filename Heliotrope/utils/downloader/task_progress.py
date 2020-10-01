import asyncio

import aiocache


class TaskProgress:
    def __init__(self) -> None:
        self.cache = aiocache.Cache()

    async def cache_task(self, user_id, count: int, task: asyncio.Task):
        task_dict_list = [{"task_name": task.get_name(), "count": count, "task": task}]
        if await self.cache.exists(user_id):
            already_in_list = await self.cache.get(user_id)
            already_in_list.extend(task_dict_list)
            await self.cache.set(user_id, already_in_list)
        else:
            await self.cache.set(user_id, task_dict_list)

    async def cache_already(self, user_id, index, count, status, link):
        already_dict_list = [
            {"index": index, "count": count, "task_status": status, "link": link}
        ]
        if await self.cache.exists(f"{user_id}_already"):
            already_in_list = await self.cache.get(f"{user_id}_already")
            already_in_list.extend(already_dict_list)
            await self.cache.set(f"{user_id}_already", already_in_list)
        else:
            await self.cache.set(f"{user_id}_already", already_dict_list)