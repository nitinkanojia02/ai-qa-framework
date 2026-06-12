from pathlib import Path
from typing import Dict

from libraries.dom_understanding_engine import DOMUnderstandingEngine
from models.page_models import PageAnalysis, PageSnapshot
from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug, utc_now_iso

logger = get_logger(__name__)

class PageAnalyzer:
    def __init__(self, artifact_manager) -> None:
        self.artifact_manager = artifact_manager
        self.dom_engine = DOMUnderstandingEngine()

    def _safe_page_name(self, title: str, url: str) -> str:
        if title and title.strip():
            raw = title.strip().lower().replace(" ", "_")
        else:
            raw = url.rstrip("/").split("/")[-1] or "home"
            raw = raw.lower().replace(" ", "_")

        sanitized = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in raw)
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")
        return sanitized.strip("_") or "page"

    def _build_metadata(self, dom_data: Dict, classified: Dict) -> Dict[str, str]:
        return {
            "forms_count": str(dom_data.get("forms_count", 0)),
            "element_count": str(dom_data.get("element_count", 0)),
            "buttons_count": str(len(classified.get("buttons", []))),
            "inputs_count": str(len(classified.get("inputs", []))),
            "links_count": str(len(classified.get("links", []))),
            "others_count": str(len(classified.get("others", []))),
        }

    def analyze_page(self, page) -> PageSnapshot:
        logger.info("Starting page analysis")

        dom_data = self.dom_engine.extract_dom_intelligence(page)
        classified = self.dom_engine.classify_elements(dom_data)

        title = dom_data.get("title", "")
        url = dom_data.get("url", "")
        page_name = self._safe_page_name(title, url)

        page_analysis = PageAnalysis(
            url=url,
            title=title,
            page_name=page_name,
            buttons=classified.get("buttons", []),
            inputs=classified.get("inputs", []),
            links=classified.get("links", []),
            forms=classified.get("forms", []),
            metadata=self._build_metadata(dom_data, classified),
        )

        snapshot = PageSnapshot(
            page_analysis=page_analysis,
            captured_at=utc_now_iso(),
        )

        self._persist_page_artifacts(page, dom_data, snapshot)

        logger.info(
            "Page analysis completed | page=%s | title=%s | url=%s",
            page_name,
            title,
            url,
        )
        return snapshot

    def _persist_page_artifacts(self, page, dom_data: Dict, snapshot: PageSnapshot) -> None:
        page_data_dir = Path(self.artifact_manager.get_path("page_data"))
        screenshot_dir = Path(self.artifact_manager.get_path("screenshots"))

        page_name = snapshot.page_analysis.page_name
        suffix = timestamp_slug()

        screenshot_path = screenshot_dir / f"{page_name}_{suffix}.png"
        dom_path = page_data_dir / f"{page_name}_{suffix}.dom.json"
        analysis_path = page_data_dir / f"{page_name}_{suffix}.analysis.json"

        page.screenshot(path=str(screenshot_path), full_page=True)
        write_json(str(dom_path), dom_data)
        write_json(str(analysis_path), snapshot.to_dict())

        snapshot.screenshot_path = str(screenshot_path)
        snapshot.dom_path = str(dom_path)

        logger.info("Saved page screenshot: %s", screenshot_path)
        logger.info("Saved page DOM: %s", dom_path)
        logger.info("Saved page analysis: %s", analysis_path)