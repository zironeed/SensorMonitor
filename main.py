import asyncio

from async_src.file_processor import get_dirs

async def main(path_to_dirs):
    await get_dirs(path_to_dirs)


if __name__ == '__main__':
    asyncio.run(main('C:/Users/zeroneed/Desktop/app/sample/'))
