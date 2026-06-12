from pathlib import Path
from typing import Dict, List, Optional, Tuple

from models.locator_models import LocatorCandidate, LocatorRecord
from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug

logger = get_logger(__name__)

class LocatorRanker:
    def __init__(self, artifact_manager, locator_config: Dict) -> None:
        self.artifact_manager = artifact_manager
        self.locator_config = locator_config
        self.ranking_order = locator_config.get(
            "ranking_order",
            ["id", "name", "data-testid", "aria-label", "placeholder", "text", "xpath"],
        )

    def generate_locator_repository(self, page_snapshot) -> List[LocatorRecord]:
        logger.info("Generating locator repository for page: %s", page_snapshot.page_analysis.page_name)

        records: List[LocatorRecord] = []

        all_elements = (
            page_snapshot.page_analysis.buttons
            + page_snapshot.page_analysis.inputs
            + page_snapshot.page_analysis.links
        )

        for index, element in enumerate(all_elements, start=1):
            element_name = self._derive_element_name(element, index)
            candidates = self._build_candidates(element)
            scored_candidates = self._score_candidates(element, candidates)

            if not scored_candidates:
                logger.warning("No locator candidates found for element: %s", element_name)
                continue

            best_locator = scored_candidates[0]
            fallback_locators = scored_candidates[1:6]

            record = LocatorRecord(
                element_name=element_name,
                tag=element.tag,
                best_locator=best_locator,
                fallback_locators=fallback_locators,
                original_text=element.text,
                original_attributes=element.attributes,
            )
            records.append(record)

        self._persist_locator_repository(page_snapshot.page_analysis.page_name, records)
        logger.info("Locator repository generated with %s records", len(records))
        return records

    def _derive_element_name(self, element, index: int) -> str:
        raw_name = (
            element.attributes.get("aria-label")
            or element.name
            or element.element_id
            or element.placeholder
            or element.text
            or f"{element.tag}_{index}"
        )
        normalized = raw_name.strip().lower().replace(" ", "_")
        normalized = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in normalized)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_") or f"{element.tag}_{index}"

    def _build_candidates(self, element) -> List[LocatorCandidate]:
        attrs = element.attributes or {}
        text = (element.text or "").strip()

        candidates: List[LocatorCandidate] = []

        if element.element_id:
            candidates.append(
                LocatorCandidate(by="id", value=element.element_id, strategy="id")
            )

        if element.name:
            candidates.append(
                LocatorCandidate(by="name", value=element.name, strategy="name")
            )

        if attrs.get("data-testid"):
            candidates.append(
                LocatorCandidate(
                    by="css",
                    value=f'[data-testid="{attrs["data-testid"]}"]',
                    strategy="data-testid",
                )
            )

        if attrs.get("aria-label"):
            candidates.append(
                LocatorCandidate(
                    by="css",
                    value=f'[aria-label="{attrs["aria-label"]}"]',
                    strategy="aria-label",
                )
            )

        if element.placeholder:
            candidates.append(
                LocatorCandidate(
                    by="css",
                    value=f'[placeholder="{element.placeholder}"]',
                    strategy="placeholder",
                )
            )

        for candidate in element.locator_candidates:
            by = candidate.get("by", "").strip()
            value = candidate.get("value", "").strip()
            if by and value:
                normalized_by = "css" if by == "css" else by
                candidates.append(
                    LocatorCandidate(by=normalized_by, value=value, strategy=by)
                )

        if text:
            safe_text = text.replace('"', '\\"')
            if element.tag == "button":
                candidates.append(
                    LocatorCandidate(
                        by="xpath",
                        value=f'//button[normalize-space()="{safe_text}"]',
                        strategy="text",
                    )
                )
            elif element.tag == "a":
                candidates.append(
                    LocatorCandidate(
                        by="xpath",
                        value=f'//a[normalize-space()="{safe_text}"]',
                        strategy="text",
                    )
                )
            else:
                candidates.append(
                    LocatorCandidate(
                        by="xpath",
                        value=f'//*[normalize-space()="{safe_text}"]',
                        strategy="text",
                    )
                )

        unique_candidates = self._deduplicate_candidates(candidates)
        return unique_candidates

    def _deduplicate_candidates(self, candidates: List[LocatorCandidate]) -> List[LocatorCandidate]:
        seen = set()
        unique = []

        for candidate in candidates:
            key = (candidate.by, candidate.value)
            if key not in seen and candidate.value:
                seen.add(key)
                unique.append(candidate)

        return unique

    def _score_candidates(self, element, candidates: List[LocatorCandidate]) -> List[LocatorCandidate]:
        scored: List[LocatorCandidate] = []

        for candidate in candidates:
            score = self._base_score(candidate.strategy)

            if element.element_id and candidate.strategy == "id":
                score += 40

            if element.name and candidate.strategy == "name":
                score += 30

            if candidate.strategy == "data-testid":
                score += 35

            if candidate.strategy == "aria-label":
                score += 25

            if candidate.strategy == "placeholder":
                score += 20

            if candidate.strategy == "text":
                text_len = len(element.text.strip()) if element.text else 0
                score += min(text_len, 15)

            if candidate.by == "xpath":
                score -= 5

            if candidate.by == "css":
                score += 5

            candidate.score = float(score)
            candidate.metadata = {
                "tag": element.tag,
                "text": element.text[:100] if element.text else "",
                "element_id": element.element_id,
                "name": element.name,
            }
            scored.append(candidate)

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored

    def _base_score(self, strategy: str) -> int:
        if strategy in self.ranking_order:
            return max(100 - (self.ranking_order.index(strategy) * 10), 10)
        return 10

    def _persist_locator_repository(self, page_name: str, records: List[LocatorRecord]) -> None:
        locator_dir = Path(self.artifact_manager.get_path("locator_intelligence"))
        suffix = timestamp_slug()
        output_path = locator_dir / f"{page_name}_{suffix}.locators.json"
        write_json(output_path.as_posix(), [record.to_dict() for record in records])
        logger.info("Saved locator repository: %s", output_path)

    def find_record_by_name(
        self,
        locator_records: List[LocatorRecord],
        element_name: str,
    ) -> Optional[LocatorRecord]:
        for record in locator_records:
            if record.element_name == element_name:
                return record
        return None