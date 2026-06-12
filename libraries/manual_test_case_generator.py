from pathlib import Path
from typing import Dict, List

from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug, utc_now_iso

logger = get_logger(__name__)


class ManualTestCaseGenerator:
    def __init__(self, artifact_manager) -> None:
        self.artifact_manager = artifact_manager
        self.output_dir = Path(self.artifact_manager.base_path) / "testcases"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_knowledge(self, knowledge) -> Dict[str, str]:
        workflow_groups = self._group_transitions(knowledge.workflow_transitions)
        test_cases = []
        markdown_sections = ["# Generated Manual Test Cases", ""]

        for index, (group_key, transitions) in enumerate(workflow_groups.items(), start=1):
            test_case = self._build_test_case(index, group_key, transitions, knowledge)
            test_cases.append(test_case)
            markdown_sections.extend(self._to_markdown(test_case))
            markdown_sections.append("")

        payload = {
            "generated_at": utc_now_iso(),
            "application_name": knowledge.application_name,
            "test_case_count": len(test_cases),
            "test_cases": test_cases,
        }

        json_path = self.output_dir / "generated_manual_test_cases.json"
        md_path = self.output_dir / "generated_manual_test_cases.md"
        snapshot_json_path = self.output_dir / f"generated_manual_test_cases_{timestamp_slug()}.json"
        snapshot_md_path = self.output_dir / f"generated_manual_test_cases_{timestamp_slug()}.md"

        write_json(json_path.as_posix(), payload)
        write_json(snapshot_json_path.as_posix(), payload)
        md_path.write_text("\n".join(markdown_sections), encoding="utf-8")
        snapshot_md_path.write_text("\n".join(markdown_sections), encoding="utf-8")

        logger.info("Generated %s manual test cases", len(test_cases))
        return {
            "json_path": json_path.as_posix(),
            "markdown_path": md_path.as_posix(),
            "count": len(test_cases),
            "test_cases": test_cases,
        }

    def _group_transitions(self, transitions: List) -> Dict[str, List]:
        grouped: Dict[str, List] = {}
        if not transitions:
            grouped["application_smoke"] = []
            return grouped

        for transition in transitions:
            workflow_type = getattr(transition, "workflow_type", "navigation") or "navigation"
            source_page = getattr(transition, "source_page", "") or "unknown_page"
            key = f"{workflow_type}:{source_page}"
            grouped.setdefault(key, []).append(transition)
        return grouped

    def _build_test_case(self, index: int, group_key: str, transitions: List, knowledge) -> Dict:
        workflow_type, source_page = group_key.split(":", 1)
        page = self._find_page(knowledge, source_page)
        title = self._build_title(index, workflow_type, page, transitions)
        objective = self._build_objective(workflow_type, page, transitions)
        preconditions = self._build_preconditions(workflow_type, page)
        steps = self._build_steps(page, transitions)
        expected_results = self._build_expected_results(page, transitions)
        tags = self._build_tags(workflow_type, page, transitions)
        linked_pages = sorted({t.source_page for t in transitions if getattr(t, 'source_page', '')} | {t.destination_page for t in transitions if getattr(t, 'destination_page', '')})

        return {
            "test_case_id": f"AUTO-MTC-{index:03d}",
            "title": title,
            "objective": objective,
            "workflow_type": workflow_type,
            "source_page": source_page,
            "module_name": getattr(page, "module_name", "") if page else "",
            "primary_entity": getattr(page, "primary_entity", "") if page else "",
            "preconditions": preconditions,
            "steps": steps,
            "expected_results": expected_results,
            "tags": tags,
            "linked_pages": linked_pages,
            "transition_count": len(transitions),
            "generation_source": "application_knowledge",
        }

    def _build_title(self, index: int, workflow_type: str, page, transitions: List) -> str:
        if workflow_type == "authentication":
            return "Validate user can authenticate successfully"
        if page and getattr(page, "business_purpose", ""):
            return f"Validate {page.business_purpose.lower()}"
        if page and getattr(page, "page_name", ""):
            return f"Validate {page.page_name.replace('_', ' ')} workflow"
        return f"Validate discovered {workflow_type.replace('_', ' ')} workflow {index}"

    def _build_objective(self, workflow_type: str, page, transitions: List) -> str:
        if page and getattr(page, "business_purpose", ""):
            return page.business_purpose
        if workflow_type == "authentication":
            return "Verify that a valid user can access the application and reach the authenticated landing experience."
        if workflow_type == "search":
            return "Verify that the user can search and navigate through discovered application states."
        if workflow_type == "data_entry":
            return "Verify that the user can enter data and progress through the discovered workflow."
        return "Verify the discovered workflow can be executed successfully from the identified starting page."

    def _build_preconditions(self, workflow_type: str, page) -> List[str]:
        preconditions = ["Application is reachable in the target environment."]
        if workflow_type != "authentication":
            preconditions.append("User is authenticated with valid credentials.")
        if page and getattr(page, "page_name", ""):
            preconditions.append(f"User can access the {page.page_name.replace('_', ' ')} page.")
        return preconditions

    def _build_steps(self, page, transitions: List) -> List[str]:
        steps = []
        if page and getattr(page, "page_name", ""):
            steps.append(f"Navigate to the {page.page_name.replace('_', ' ')} page.")
        else:
            steps.append("Navigate to the discovered workflow starting point.")

        if not transitions:
            steps.append("Observe the landing page and verify key elements are displayed.")
            return steps

        for transition in transitions:
            action = getattr(transition, "action", "interact") or "interact"
            target = getattr(transition, "target", "target element") or "target element"
            destination = getattr(transition, "destination_page", "")
            transition_intent = getattr(transition, "transition_intent", "navigation")

            human_action = self._humanize_action(action, target, transition_intent)
            steps.append(human_action)
            if destination:
                steps.append(f"Observe that the application transitions to {destination.replace('_', ' ')}.")
        return steps

    def _build_expected_results(self, page, transitions: List) -> List[str]:
        results = ["The workflow executes without unexpected errors."]
        if page and getattr(page, "page_type", ""):
            results.append(f"The expected {page.page_type.replace('_', ' ')} experience is displayed.")
        if transitions:
            last_transition = transitions[-1]
            destination = getattr(last_transition, "destination_page", "")
            if destination:
                results.append(f"The user reaches {destination.replace('_', ' ')} successfully.")
        results.append("Relevant controls, data, and navigation options are visible and usable.")
        return results

    def _build_tags(self, workflow_type: str, page, transitions: List) -> List[str]:
        tags = ["ai-generated", "manual-test", workflow_type]
        if page and getattr(page, "module_name", ""):
            tags.append(page.module_name.lower().replace(" ", "_"))
        if page and getattr(page, "primary_entity", ""):
            tags.append(page.primary_entity.lower().replace(" ", "_"))
        if any(getattr(t, "workflow_type", "") == "approval" for t in transitions):
            tags.append("high-risk")
        return sorted(set(tags))

    def _find_page(self, knowledge, page_name: str):
        for page in knowledge.pages:
            if page.page_name == page_name:
                return page
        return None

    def _humanize_action(self, action: str, target: str, intent: str) -> str:
        target_text = target.replace("_", " ") if target else "target element"
        action_text = action.replace("_", " ") if action else "interact"

        if intent == "authentication":
            return f"Authenticate using the {target_text} control as required."
        if intent == "search":
            return f"Use the {target_text} control to perform a search action."
        if intent == "approval":
            return f"Use the {target_text} control to complete the approval-related action carefully."
        if intent == "data_entry":
            return f"Use the {target_text} control to enter or submit required data."
        return f"Perform the {action_text} action on {target_text}."

    def _to_markdown(self, test_case: Dict) -> List[str]:
        lines = [
            f"## {test_case['test_case_id']} - {test_case['title']}",
            "",
            f"**Objective:** {test_case['objective']}",
            f"**Workflow Type:** {test_case['workflow_type']}",
            f"**Module:** {test_case['module_name'] or 'unknown'}",
            f"**Primary Entity:** {test_case['primary_entity'] or 'unknown'}",
            f"**Tags:** {', '.join(test_case['tags'])}",
            "",
            "### Preconditions",
        ]
        lines.extend([f"- {item}" for item in test_case["preconditions"]])
        lines.append("")
        lines.append("### Steps")
        lines.extend([f"{idx}. {item}" for idx, item in enumerate(test_case["steps"], start=1)])
        lines.append("")
        lines.append("### Expected Results")
        lines.extend([f"- {item}" for item in test_case["expected_results"]])
        return lines
