import sys
import logging
import asyncio
from src.database_handler import database_handler
import src.app as app


async def main() -> None:
    await app.dp.start_polling(app.bot)


if __name__ == "__main__":
    database_handler
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
