from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from utils.logger import get_logger
from utils.time_utils import timestamp_slug, utc_now_iso

logger = get_logger(__name__)


class RobotTestGenerator:
    def __init__(self, artifact_manager) -> None:
        self.artifact_manager = artifact_manager
        self.output_dir = Path(self.artifact_manager.get_path("generated_robot_tests"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_manual_test_cases(self, manual_test_case_artifacts: Dict[str, str], knowledge) -> Dict[str, str]:
        test_cases = manual_test_case_artifacts.get("test_cases", [])
        if not test_cases:
            test_cases = self._build_fallback_test_cases(knowledge)

        knowledge_index = self._build_knowledge_index(knowledge)
        suite_content = self._build_suite_content(test_cases, knowledge_index)
        resource_content = self._build_resource_content(knowledge_index)
        variable_content = self._build_variable_content()

        suite_path = self.output_dir / "generated_workflows.robot"
        resource_path = self.output_dir / "generated_keywords.resource"
        variables_path = self.output_dir / "generated_variables.resource"
        timestamp = timestamp_slug()
        snapshot_suite_path = self.output_dir / f"generated_workflows_{timestamp}.robot"
        snapshot_resource_path = self.output_dir / f"generated_keywords_{timestamp}.resource"
        snapshot_variables_path = self.output_dir / f"generated_variables_{timestamp}.resource"

        suite_path.write_text(suite_content, encoding="utf-8")
        resource_path.write_text(resource_content, encoding="utf-8")
        variables_path.write_text(variable_content, encoding="utf-8")
        snapshot_suite_path.write_text(suite_content, encoding="utf-8")
        snapshot_resource_path.write_text(resource_content, encoding="utf-8")
        snapshot_variables_path.write_text(variable_content, encoding="utf-8")

        logger.info("Generated %s Robot Framework test cases", len(test_cases))
        return {
            "suite_path": suite_path.as_posix(),
            "resource_path": resource_path.as_posix(),
            "variables_path": variables_path.as_posix(),
            "count": len(test_cases),
            "generated_at": utc_now_iso(),
            "keyword_count": len(knowledge_index["action_keywords"]),
            "locator_count": len(knowledge_index["locators"]),
        }

    def _build_suite_content(self, test_cases: List[Dict], knowledge_index: Dict) -> str:
        lines = [
            "*** Settings ***",
            "Documentation    AI-generated Robot Framework suite from discovered application knowledge.",
            "Resource    generated_keywords.resource",
            "Suite Setup    Open Generated Application Session",
            "Suite Teardown    Close Generated Application Session",
            "Test Setup    Prepare Generated Test Context",
            "",
            "*** Test Cases ***",
        ]

        for test_case in test_cases:
            lines.extend(self._render_robot_test_case(test_case, knowledge_index))
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    def _build_resource_content(self, knowledge_index: Dict) -> str:
        lines = [
            "*** Settings ***",
            "Documentation    Generated keyword and locator resource from application knowledge.",
            "Library    BuiltIn",
            "Library    SeleniumLibrary",
            "Resource    generated_variables.resource",
            "",
            "*** Variables ***",
        ]

        for locator_name, locator_value in knowledge_index["locators"].items():
            lines.append(f"${{{locator_name}}}    {locator_value}")

        lines.extend([
            "",
            "*** Keywords ***",
            "Open Generated Application Session",
            "    ${browser}=    Get Variable Value    ${BROWSER}    chrome",
            "    Open Browser    ${APP_BASE_URL}    ${browser}",
            "    Maximize Browser Window",
            "    Run Keyword If    '${APP_USERNAME}' != '' and '${APP_PASSWORD}' != ''    Perform Generated Login",
            "",
            "Close Generated Application Session",
            "    Close All Browsers",
            "",
            "Prepare Generated Test Context",
            "    Log    Prepare generated test context for execution",
            "",
            "Open Generated Workflow Start",
            "    Go To    ${APP_BASE_URL}",
            "",
            "Perform Generated Login",
            "    ${username_locator}=    Get Variable Value    ${LOGIN_USERNAME_LOCATOR}    ${EMPTY}",
            "    ${password_locator}=    Get Variable Value    ${LOGIN_PASSWORD_LOCATOR}    ${EMPTY}",
            "    ${submit_locator}=    Get Variable Value    ${LOGIN_SUBMIT_LOCATOR}    ${EMPTY}",
            "    Run Keyword If    '${username_locator}' != ''    Wait Until Element Is Visible    ${username_locator}    timeout=10s",
            "    Run Keyword If    '${username_locator}' != ''    Input Text    ${username_locator}    ${APP_USERNAME}",
            "    Run Keyword If    '${password_locator}' != ''    Wait Until Element Is Visible    ${password_locator}    timeout=10s",
            "    Run Keyword If    '${password_locator}' != ''    Input Text    ${password_locator}    ${APP_PASSWORD}",
            "    Run Keyword If    '${submit_locator}' != ''    Click Element    ${submit_locator}",
            "",
            "Use Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Get Variable Value    ${${locator_name}}    ${EMPTY}",
            "    Log    Using learned locator ${locator_name}: ${locator}",
            "    [Return]    ${locator}",
            "",
            "Click Using Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    Run Keyword If    '${locator}' == ''    Fail    Learned locator ${locator_name} is empty",
            "    Wait Until Element Is Visible    ${locator}    timeout=10s",
            "    Click Element    ${locator}",
            "",
            "Input Text Using Known Locator",
            "    [Arguments]    ${locator_name}    ${value}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    Run Keyword If    '${locator}' == ''    Fail    Learned locator ${locator_name} is empty",
            "    Wait Until Element Is Visible    ${locator}    timeout=10s",
            "    Input Text    ${locator}    ${value}",
            "",
            "Assert Element Using Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    Run Keyword If    '${locator}' == ''    Fail    Learned locator ${locator_name} is empty",
            "    Wait Until Element Is Visible    ${locator}    timeout=10s",
            "    Element Should Be Visible    ${locator}",
            "",
            "Perform Generated Step",
            "    [Arguments]    ${step}",
            "    Log    Execute generated step: ${step}",
            "",
            "Validate Generated Outcome",
            "    [Arguments]    ${expected}",
            "    Log    Validate generated outcome: ${expected}",
            "",
        ])

        for keyword_name, keyword_data in knowledge_index["action_keywords"].items():
            lines.extend(self._render_action_keyword(keyword_name, keyword_data))

        return "\n".join(lines).strip() + "\n"

    def _render_robot_test_case(self, test_case: Dict, knowledge_index: Dict) -> List[str]:
        title = self._robot_safe_name(test_case.get("title", "Generated Workflow"))
        tags = test_case.get("tags", [])
        steps = test_case.get("steps", [])
        expected_results = test_case.get("expected_results", [])
        module_name = test_case.get("module_name", "")

        lines = [title]
        if tags:
            lines.append(f"    [Tags]    {'    '.join(tags)}")
        lines.append("    Open Generated Workflow Start")

        mapped_keyword = self._select_keyword_for_test_case(test_case, knowledge_index)
        if mapped_keyword:
            lines.append(f"    {mapped_keyword}")
        elif module_name:
            safe_module = module_name.replace("${", "$\\{")
            lines.append(f"    Perform Generated Step    Navigate within module: {safe_module}")

        for step in steps:
            safe_step = step.replace("${", "$\\{")
            lines.append(f"    Perform Generated Step    {safe_step}")

        for expected in expected_results:
            safe_expected = expected.replace("${", "$\\{")
            lines.append(f"    Validate Generated Outcome    {safe_expected}")
        return lines

    def _build_variable_content(self) -> str:
        framework_config = self._load_framework_config()
        application = framework_config.get("application", {})
        authentication = framework_config.get("authentication", {})

        lines = [
            "*** Variables ***",
            f"${{APP_BASE_URL}}    {self._robot_scalar(application.get('base_url', ''))}",
            f"${{APP_USERNAME}}    {self._robot_scalar(authentication.get('username', ''))}",
            f"${{APP_PASSWORD}}    {self._robot_scalar(authentication.get('password', ''))}",
            f"${{BROWSER}}    {self._robot_scalar('chrome')}",
            f"${{LOGIN_USERNAME_LOCATOR}}    {self._robot_scalar(self._selector_to_selenium_locator(authentication.get('username_selector_type', ''), authentication.get('username_selector', '')))}",
            f"${{LOGIN_PASSWORD_LOCATOR}}    {self._robot_scalar(self._selector_to_selenium_locator(authentication.get('password_selector_type', ''), authentication.get('password_selector', '')))}",
            f"${{LOGIN_SUBMIT_LOCATOR}}    {self._robot_scalar(self._selector_to_selenium_locator(authentication.get('submit_selector_type', ''), authentication.get('submit_selector', '')))}",
        ]
        return "\n".join(lines).strip() + "\n"

    def _build_knowledge_index(self, knowledge) -> Dict:
        locator_map = {}
        action_keywords = {}

        for locator in knowledge.locators:
            locator_name = self._locator_variable_name(locator.page_name, locator.element_name)
            locator_value = self._serialize_locator(locator.best_locator)
            if locator_value:
                locator_map[locator_name] = locator_value

        for element in knowledge.elements:
            if element.intent not in {"authentication", "search", "data_submission", "edit", "approval", "destructive", "data_entry", "navigation_or_action"}:
                continue
            keyword_name = self._keyword_name(element.page_name, element.element_name, element.intent)
            locator_variable = self._locator_variable_name(element.page_name, element.element_name)
            action_keywords[keyword_name] = {
                "page_name": element.page_name,
                "element_name": element.element_name,
                "element_type": element.element_type,
                "intent": element.intent,
                "locator_variable": locator_variable if locator_variable in locator_map else "",
                "description": f"Interact with {element.element_name} on {element.page_name} for intent {element.intent}",
            }

        return {
            "locators": locator_map,
            "action_keywords": action_keywords,
        }

    def _select_keyword_for_test_case(self, test_case: Dict, knowledge_index: Dict) -> str:
        title = (test_case.get("title") or "").lower()
        module_name = (test_case.get("module_name") or "").lower()
        workflow_type = (test_case.get("workflow_type") or "").lower()

        for keyword_name, keyword_data in knowledge_index["action_keywords"].items():
            page_name = keyword_data["page_name"].lower()
            intent = keyword_data["intent"].lower()
            element_name = keyword_data["element_name"].lower()
            if page_name in title or page_name in module_name:
                return keyword_name
            if element_name and element_name in title:
                return keyword_name
            if workflow_type and workflow_type in intent:
                return keyword_name
        return ""

    def _render_action_keyword(self, keyword_name: str, keyword_data: Dict) -> List[str]:
        lines = [keyword_name]
        lines.append(f"    Log    Execute learned action for page: {keyword_data['page_name']}")
        action_type, default_value = self._keyword_action_strategy(keyword_data)
        locator_variable = keyword_data.get("locator_variable")

        if action_type == "input":
            lines.append("    ${generated_value}=    Set Variable    AI_GENERATED_VALUE")
            if default_value:
                lines.append(f"    ${generated_value}=    Set Variable    {default_value}")
            if locator_variable:
                lines.append(f"    Input Text Using Known Locator    {locator_variable}    ${'{'}generated_value{'}'}")
            else:
                lines.append(f"    Perform Generated Step    {keyword_data['description']}")
        elif action_type == "assert":
            if locator_variable:
                lines.append(f"    Assert Element Using Known Locator    {locator_variable}")
            else:
                lines.append(f"    Validate Generated Outcome    {keyword_data['description']}")
        else:
            if locator_variable:
                lines.append(f"    Click Using Known Locator    {locator_variable}")
            else:
                lines.append(f"    Perform Generated Step    {keyword_data['description']}")

        lines.append(f"    Perform Generated Step    {keyword_data['description']}")
        lines.append("")
        return lines

    def _keyword_action_strategy(self, keyword_data: Dict) -> Tuple[str, str]:
        intent = (keyword_data.get("intent") or "").lower()
        element_name = (keyword_data.get("element_name") or "").lower()
        element_type = (keyword_data.get("element_type") or "").lower()

        if intent in {"data_entry", "search", "authentication"} or element_type == "input":
            if "password" in element_name:
                return "input", "AI_GENERATED_PASSWORD"
            if "user" in element_name or "email" in element_name:
                return "input", "AI_GENERATED_USER"
            if "search" in element_name:
                return "input", "AI_SEARCH_TERM"
            return "input", "AI_GENERATED_VALUE"

        if intent in {"approval", "destructive"}:
            return "click", ""

        if "dashboard" in element_name or "message" in element_name or "success" in element_name:
            return "assert", ""

        return "click", ""

    def _serialize_locator(self, locator: Dict) -> str:
        locator_type = (locator or {}).get("locator_type", "")
        locator_value = (locator or {}).get("locator_value", "")
        if not locator_value:
            return ""
        return self._selector_to_selenium_locator(locator_type, locator_value)

    def _selector_to_selenium_locator(self, locator_type: str, locator_value: str) -> str:
        if not locator_value:
            return ""
        locator_type = (locator_type or "").strip().lower()
        if locator_type in {"xpath", "css", "id", "name", "link", "partial link"}:
            return f"{locator_type}={locator_value}"
        if locator_type == "text":
            return f"xpath=//*[normalize-space()='{locator_value}']"
        return locator_value

    def _load_framework_config(self) -> Dict:
        config_path = Path("config/framework_config.yaml")
        if not config_path.exists():
            return {}
        try:
            return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            logger.warning("Unable to load framework config for Robot variable generation: %s", exc)
            return {}

    def _robot_scalar(self, value: str) -> str:
        return (value or "").replace("\n", " ")

    def _locator_variable_name(self, page_name: str, element_name: str) -> str:
        return f"LOCATOR_{self._slug(page_name)}_{self._slug(element_name)}"

    def _keyword_name(self, page_name: str, element_name: str, intent: str) -> str:
        return self._robot_safe_name(f"Perform {intent} on {element_name} in {page_name}")

    def _slug(self, value: str) -> str:
        cleaned = "_".join((value or "unknown").lower().split())
        cleaned = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in cleaned)
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        return cleaned.strip("_") or "unknown"

    def _robot_safe_name(self, value: str) -> str:
        cleaned = " ".join(value.replace("_", " ").split())
        return cleaned or "Generated Workflow"

    def _build_fallback_test_cases(self, knowledge) -> List[Dict]:
        fallback_steps = ["Observe the discovered landing page.", "Verify important elements are visible."]
        fallback_results = ["The page is reachable.", "Core controls are displayed."]
        return [
            {
                "title": f"Validate discovered {knowledge.application_name} landing workflow",
                "tags": ["ai-generated", "robot-generated", "smoke"],
                "steps": fallback_steps,
                "expected_results": fallback_results,
            }
        ]
