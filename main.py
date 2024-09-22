import asyncio
import sys
from PyQt5.QtWidgets import QApplication
from async_src.draw_master import SensorMonitor


async def main():
    app = QApplication(sys.argv)
    window = SensorMonitor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    asyncio.run(main())
