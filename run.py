import asyncio
import signal
import sys

from app import create_app

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main():
    if "win" in sys.platform:
        # Fix handling of keyboard interrupts with asyncio in windows
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = create_app()
    # access_logger = logging.getLogger("aiohttp.access")
    app.run(port=9090, debug=True,host='0.0.0.0')


if __name__ == "__main__":
    main()
