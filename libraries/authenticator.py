import time
from typing import Dict

from utils.logger import get_logger

logger = get_logger(__name__)

class AuthenticationError(Exception):
    """Raised when authentication fails."""

class Authenticator:
    def __init__(self, auth_config: Dict) -> None:
        self.auth_config = auth_config

    def is_enabled(self) -> bool:
        return self.auth_config.get("enabled", False)

    def login(self, page) -> Dict:
        if not self.is_enabled():
            logger.info("Authentication is disabled in config")
            return {
                "enabled": False,
                "status": "skipped",
                "reason": "authentication_disabled",
            }

        username = self.auth_config.get("username", "")
        password = self.auth_config.get("password", "")

        pre_login_click_required = self.auth_config.get("pre_login_click_required", False)
        pre_login_click_selector = self.auth_config.get("pre_login_click_selector", "")
        pre_login_click_type = self.auth_config.get("pre_login_click_type", "xpath")

        username_selector = self.auth_config.get("username_selector", "")
        username_selector_type = self.auth_config.get("username_selector_type", "xpath")

        password_selector = self.auth_config.get("password_selector", "")
        password_selector_type = self.auth_config.get("password_selector_type", "xpath")

        submit_selector = self.auth_config.get("submit_selector", "")
        submit_selector_type = self.auth_config.get("submit_selector_type", "xpath")

        success_url_contains = self.auth_config.get("success_url_contains", "")
        success_selector = self.auth_config.get("success_selector", "")
        success_selector_type = self.auth_config.get("success_selector_type", "xpath")
        post_login_wait_seconds = self.auth_config.get("post_login_wait_seconds", 5)

        if not all([username_selector, password_selector, submit_selector]):
            raise AuthenticationError("Authentication config is incomplete.")

        logger.info("Starting login flow")

        if pre_login_click_required:
            logger.info("Executing pre-login click step")
            pre_login_locator = self._resolve_locator(page, pre_login_click_selector, pre_login_click_type)
            self._prepare_element(pre_login_locator)
            pre_login_locator.click()
            time.sleep(2)

        username_locator = self._resolve_locator(page, username_selector, username_selector_type)
        self._prepare_element(username_locator)
        username_locator.fill(username)

        password_locator = self._resolve_locator(page, password_selector, password_selector_type)
        self._prepare_element(password_locator)
        password_locator.fill(password)

        submit_locator = self._resolve_locator(page, submit_selector, submit_selector_type)
        self._prepare_element(submit_locator)
        submit_locator.click()

        login_success = False

        if success_selector:
            try:
                success_locator = self._resolve_locator(page, success_selector, success_selector_type)
                success_locator.wait_for(state="visible", timeout=15000)
                login_success = True
            except Exception:
                pass

        if not login_success and success_url_contains:
            end_time = time.time() + max(post_login_wait_seconds, 5)
            while time.time() < end_time:
                if success_url_contains in page.url:
                    login_success = True
                    break
                time.sleep(1)

        time.sleep(post_login_wait_seconds)

        current_url = page.url
        page_title = page.title()

        if not login_success:
            raise AuthenticationError(
                f"Login could not be verified. Current URL: {current_url} | Title: {page_title}"
            )

        logger.info("Login successful | url=%s | title=%s", current_url, page_title)

        return {
            "enabled": True,
            "status": "passed",
            "current_url": current_url,
            "title": page_title,
        }

    def _prepare_element(self, locator) -> None:
        locator.wait_for(state="attached", timeout=10000)
        try:
            locator.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        locator.wait_for(state="visible", timeout=10000)

    def _resolve_locator(self, page, selector: str, selector_type: str):
        selector_type = (selector_type or "xpath").lower().strip()

        if selector_type == "xpath":
            return page.locator(f"xpath={selector}")
        if selector_type == "css":
            return page.locator(selector)
        if selector_type == "text":
            return page.get_by_text(selector, exact=False)

        raise ValueError(f"Unsupported selector type: {selector_type}")