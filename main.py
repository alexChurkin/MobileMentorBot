import sys
import logging
import asyncio
import src.app as app


async def main() -> None:
    await app.dp.start_polling(app.bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
