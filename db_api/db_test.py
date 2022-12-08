import asyncio

from db_api import quick_commands as commands, config
from db_api.db_gino import db

async def db_test():
    await db.set_bind(config.POSTGRES_URI)
    await db.gino.drop_all()
    await db.gino.create_all()

    await commands.add_user(1,'vlad','net')
    await commands.add_user(213213,'dfdd','Some name')
    users = await commands.select_all_users()
    print(users)

    count=await commands.count_users()
    print(count)

    user= await commands.select_user(1)
    print(user)

    await commands.update_user_name(1,'vladik')

loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())