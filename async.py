import asyncio
import datetime
import aiohttp
import re
import json
from more_itertools import chunked
from typing import List
from models import SwapiPeople, async_session, init_db, drop_db


CHUNK_SIZE = 10


async def extract_values(data, target_keys: list):
    result = ""

    async def recursive_extract(node, session):
        nonlocal result
        if isinstance(node, list):
            for item in node:
                await recursive_extract(item, session)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in target_keys:
                    result = result + value
                await recursive_extract(value, session)

    async with aiohttp.ClientSession() as session:
        await recursive_extract(data, session)

    return result


async def get_item(item_type, item_list, session):
    for i, item in enumerate(item_list):
        match = re.search(r"/(\d+)/$", item)
        item_number = match.group(1)
        response = await session.get(
            f"http://swapi.py4e.com/api/{item_type}/{item_number}/"
        )
        item_list[i] = await response.json()
        item_list[i] = await extract_values(item_list[i], ["name", "title"])
    return item_list


async def get_people(item_id, session):
    response = await session.get(f"http://swapi.py4e.com/api/people/{item_id}/")
    if response.status == 200:
        people_data = await response.json()
        for item_type, item_list in people_data.items():
            if isinstance(item_list, list):
                await get_item(item_type, item_list, session)
        return people_data


async def insert_to_db(people_dict: List[dict]):
    async with async_session() as session:
        people = [SwapiPeople(**person) for person in people_dict if person is not None]
        session.add_all(people)
        await session.commit()


async def main():
    await drop_db()
    await init_db()
    session = aiohttp.ClientSession()

    for i in chunked(range(1, 101), CHUNK_SIZE):
        coros = [get_people(person_id, session) for person_id in i]
        result = await asyncio.gather(*coros)
        asyncio.create_task(insert_to_db(result))

    await session.close()
    all_tasks = asyncio.all_tasks() - {asyncio.current_task()}
    await asyncio.gather(*all_tasks)


if __name__ == "__main__":
    asyncio.run(main())
