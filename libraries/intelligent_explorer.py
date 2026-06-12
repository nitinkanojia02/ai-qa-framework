import time
from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)

class IntelligentExplorer:
    def __init__(
        self,
        self_healing_locator,
        workflow_agent,
        navigation_predictor,
        workflow_memory,
        loop_detector,
        max_actions: int = 5,
    ) -> None:
        self.self_healing_locator = self_healing_locator
        self.workflow_agent = workflow_agent
        self.navigation_predictor = navigation_predictor
        self.workflow_memory = workflow_memory
        self.loop_detector = loop_detector
        self.max_actions = max_actions

    def explore(self, page, locator_records: List) -> Dict:
        logger.info("Starting intelligent exploration")
        candidates = self.workflow_agent.build_action_candidates(locator_records)

        attempted_count = 0
        successful_count = 0
        failed_count = 0
        skipped_count = 0

        remaining_candidates = candidates[:]
        explored_actions = []

        while remaining_candidates and attempted_count < self.max_actions:
            candidate = self.navigation_predictor.predict_next_action(remaining_candidates)
            if not candidate:
                break

            remaining_candidates.remove(candidate)

            record = candidate["locator_record"]
            state_key = f"{page.url}|{record.element_name}"

            if self.workflow_memory.has_state_been_visited(state_key):
                skipped_count += 1
                logger.info("Skipping already visited state: %s", state_key)
                continue

            if self.loop_detector.is_looping(state_key):
                skipped_count += 1
                logger.info("Skipping looped state: %s", state_key)
                continue

            self.workflow_memory.mark_state_visited(state_key)
            self.loop_detector.record(state_key)

            source_url = page.url
            source_title = page.title()
            source_page = source_title or source_url

            attempted_count += 1

            try:
                element = self.self_healing_locator.find_element(page, record)
                element.click(timeout=5000)
                time.sleep(2)

                destination_url = page.url
                destination_title = page.title()
                destination_page = destination_title or destination_url

                changed = (source_url != destination_url) or (source_title != destination_title)

                status = "passed" if changed else "no_navigation_change"
                if changed:
                    successful_count += 1
                else:
                    failed_count += 1

                self.workflow_memory.add_transition(
                    action="click",
                    target=record.element_name,
                    source_page=source_page,
                    destination_page=destination_page,
                    locator=record.best_locator.to_dict(),
                    status=status,
                    metadata={
                        "source_url": source_url,
                        "destination_url": destination_url,
                    },
                )

                explored_actions.append(
                    {
                        "element_name": record.element_name,
                        "status": status,
                        "source_url": source_url,
                        "destination_url": destination_url,
                    }
                )

                if changed and destination_url != source_url:
                    try:
                        page.go_back(timeout=5000)
                        time.sleep(2)
                    except Exception as back_exc:
                        logger.warning("Could not navigate back after exploration: %s", back_exc)

            except Exception as exc:
                failed_count += 1
                logger.warning("Exploration failed for element %s: %s", record.element_name, exc)

                self.workflow_memory.add_transition(
                    action="click",
                    target=record.element_name,
                    source_page=source_page,
                    destination_page=source_page,
                    locator=record.best_locator.to_dict(),
                    status="failed",
                    metadata={"error": str(exc), "source_url": source_url},
                )

                explored_actions.append(
                    {
                        "element_name": record.element_name,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        logger.info(
            "Exploration complete | attempted=%s | successful=%s | failed=%s | skipped=%s",
            attempted_count,
            successful_count,
            failed_count,
            skipped_count,
        )

        return {
            "candidate_count": len(candidates),
            "attempted_count": attempted_count,
            "successful_count": successful_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "explored_actions": explored_actions,
        }