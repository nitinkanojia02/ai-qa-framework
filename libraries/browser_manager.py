from typing import Any, Dict, Optional
import ctypes

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    def __init__(self, browser_config: Dict[str, Any]) -> None:
        self.browser_config = browser_config
        self._playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Page:
        browser_type = self.browser_config.get("browser", "chromium")
        headless = self.browser_config.get("headless", False)
        ignore_https_errors = self.browser_config.get("ignore_https_errors", True)
        slow_mo = self.browser_config.get("slow_mo", 0)

        logger.info(
            "Starting browser: %s | headless=%s",
            browser_type,
            headless,
        )

        self._playwright = sync_playwright().start()
        browser_launcher = getattr(self._playwright, browser_type)

        launch_kwargs = {
            "headless": headless,
            "slow_mo": slow_mo,
        }

        if browser_type == "chromium":
            try:
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)

                launch_kwargs["args"] = [
                    "--start-maximized",
                    "--window-position=0,0",
                    f"--window-size={screen_width},{screen_height}",
                ]

                logger.info(
                    "Launching browser with screen size %sx%s",
                    screen_width,
                    screen_height,
                )
            except Exception as exc:
                logger.warning(
                    "Could not determine screen size, falling back to start-maximized: %s",
                    exc,
                )
                launch_kwargs["args"] = ["--start-maximized"]

        self.browser = browser_launcher.launch(**launch_kwargs)

        self.context = self.browser.new_context(
            ignore_https_errors=ignore_https_errors,
            viewport=None,
        )

        self.page = self.context.new_page()
        return self.page

    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> Page:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")

        logger.info("Navigating to URL: %s", url)
        self.page.goto(url, wait_until=wait_until)
        return self.page

    def maximize(self) -> None:
        logger.info("Browser launched in maximized mode.")

    def capture_screenshot(self, path: str, full_page: bool = True) -> str:
        if not self.page:
            raise RuntimeError("Browser has not been started. Call start() first.")

        self.page.screenshot(path=path, full_page=full_page)
        logger.info("Captured screenshot: %s", path)
        return path

    def close(self) -> None:
        logger.info("Closing browser resources")

        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self._playwright:
            self._playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self._playwright = None