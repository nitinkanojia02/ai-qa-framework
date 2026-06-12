from typing import List, Optional

from models.locator_models import LocatorCandidate, LocatorRecord
from utils.logger import get_logger

logger = get_logger(__name__)

class SelfHealingLocator:
    def __init__(self) -> None:
        logger.info("SelfHealingLocator initialized")

    def find_element(self, page, locator_record: LocatorRecord):
        logger.info("Attempting self-healing lookup for element: %s", locator_record.element_name)

        ordered_candidates: List[LocatorCandidate] = [
            locator_record.best_locator,
            *locator_record.fallback_locators,
        ]

        last_error: Optional[Exception] = None

        for candidate in ordered_candidates:
            try:
                locator = self._build_playwright_locator(page, candidate)
                count = locator.count()

                if count == 0:
                    logger.info(
                        "Locator not matched | element=%s | by=%s | value=%s",
                        locator_record.element_name,
                        candidate.by,
                        candidate.value,
                    )
                    continue

                first = locator.first
                first.wait_for(state="attached", timeout=5000)

                try:
                    first.scroll_into_view_if_needed(timeout=5000)
                except Exception:
                    pass

                first.wait_for(state="visible", timeout=5000)

                clickable_target = self._resolve_clickable_target(first)

                if clickable_target:
                    logger.info(
                        "Locator matched successfully | element=%s | strategy=%s | by=%s | value=%s",
                        locator_record.element_name,
                        candidate.strategy,
                        candidate.by,
                        candidate.value,
                    )
                    return clickable_target

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Locator attempt failed | element=%s | strategy=%s | by=%s | value=%s | error=%s",
                    locator_record.element_name,
                    candidate.strategy,
                    candidate.by,
                    candidate.value,
                    exc,
                )

        if last_error:
            raise RuntimeError(
                f"Self-healing failed for element '{locator_record.element_name}'. "
                f"Last error: {last_error}"
            )

        raise RuntimeError(f"Self-healing failed for element '{locator_record.element_name}'. No locator matched.")

    def _resolve_clickable_target(self, locator):
        try:
            locator.wait_for(state="visible", timeout=3000)
        except Exception:
            return None

        preferred_parent_selectors = [
            "xpath=ancestor::ion-fab-button[1]",
            "xpath=ancestor::ion-button[1]",
            "xpath=ancestor::ion-chip[1]",
            "xpath=ancestor::button[1]",
            "xpath=ancestor::a[1]",
            "xpath=ancestor::*[contains(@class,'ion-activatable')][1]",
        ]

        for selector in preferred_parent_selectors:
            try:
                parent = locator.locator(selector)
                if parent.count() > 0 and parent.first.is_visible():
                    try:
                        parent.first.scroll_into_view_if_needed(timeout=3000)
                    except Exception:
                        pass
                    return parent.first
            except Exception:
                continue

        return locator

    def _build_playwright_locator(self, page, candidate: LocatorCandidate):
        by = candidate.by
        value = candidate.value

        if by == "id":
            return page.locator(f'#{value}')
        if by == "name":
            return page.locator(f'[name="{value}"]')
        if by == "css":
            return page.locator(value)
        if by == "xpath":
            return page.locator(f'xpath={value}')

        raise ValueError(f"Unsupported locator type for Playwright: {by}")