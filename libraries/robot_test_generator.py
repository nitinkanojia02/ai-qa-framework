from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from utils.logger import get_logger
from utils.time_utils import timestamp_slug, utc_now_iso

logger = get_logger(__name__)


class RobotTestGenerator:
    def __init__(self, artifact_manager, framework_config: Dict | None = None) -> None:
        self.artifact_manager = artifact_manager
        self.framework_config = framework_config or {}
        self.output_dir = Path(self.artifact_manager.get_path("generated_robot_tests"))
        self.pages_dir = self.output_dir / "pages"
        self.flows_dir = self.output_dir / "flows"
        self.suites_dir = self.output_dir / "suites"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.flows_dir.mkdir(parents=True, exist_ok=True)
        self.suites_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_manual_test_cases(self, manual_test_case_artifacts: Dict[str, str], knowledge) -> Dict[str, str]:
        test_cases = manual_test_case_artifacts.get("test_cases", [])
        if not test_cases:
            test_cases = self._build_fallback_test_cases(knowledge)

        knowledge_index = self._build_knowledge_index(knowledge)
        root_resource_content = self._build_root_resource_content(knowledge_index)
        variable_content = self._build_variable_content()
        page_resource_paths = self._write_page_resources(knowledge_index)
        flow_resource_paths = self._write_flow_resources(test_cases, knowledge_index)
        suite_content = self._build_root_suite_content(test_cases, knowledge_index)
        modular_suite_paths = self._write_modular_suites(test_cases, knowledge_index)

        suite_path = self.output_dir / "generated_workflows.robot"
        resource_path = self.output_dir / "generated_keywords.resource"
        variables_path = self.output_dir / "generated_variables.resource"
        timestamp = timestamp_slug()
        snapshot_suite_path = self.output_dir / f"generated_workflows_{timestamp}.robot"
        snapshot_resource_path = self.output_dir / f"generated_keywords_{timestamp}.resource"
        snapshot_variables_path = self.output_dir / f"generated_variables_{timestamp}.resource"

        suite_path.write_text(suite_content, encoding="utf-8")
        resource_path.write_text(root_resource_content, encoding="utf-8")
        variables_path.write_text(variable_content, encoding="utf-8")
        snapshot_suite_path.write_text(suite_content, encoding="utf-8")
        snapshot_resource_path.write_text(root_resource_content, encoding="utf-8")
        snapshot_variables_path.write_text(variable_content, encoding="utf-8")

        logger.info("Generated %s Robot Framework test cases", len(test_cases))
        return {
            "suite_path": suite_path.as_posix(),
            "resource_path": resource_path.as_posix(),
            "variables_path": variables_path.as_posix(),
            "page_resource_paths": page_resource_paths,
            "flow_resource_paths": flow_resource_paths,
            "suite_paths": modular_suite_paths,
            "count": len(test_cases),
            "generated_at": utc_now_iso(),
            "keyword_count": len(knowledge_index["action_keywords"]),
            "locator_count": len(knowledge_index["locators"]),
        }

    def _build_root_suite_content(self, test_cases: List[Dict], knowledge_index: Dict) -> str:
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

    def _build_root_resource_content(self, knowledge_index: Dict) -> str:
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
            "    ${start_url}=    Get Variable Value    ${APP_BASE_URL}    ${EMPTY}",
            "    Open Browser    ${start_url}    ${browser}",
            "    Maximize Browser Window",
            "    ${login_needed}=    Is Generated Login Required",
            "    IF    $login_needed and $APP_USERNAME and $APP_PASSWORD",
            "        ${login_url}=    Get Variable Value    ${APP_LOGIN_URL}    ${EMPTY}",
            "        IF    $login_url",
            "            Go To    ${login_url}",
            "        END",
            "        Perform Generated Login",
            "    END",
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
            "Is Generated Login Required",
            "    ${username_locator}=    Get Variable Value    ${LOGIN_USERNAME_LOCATOR}    ${EMPTY}",
            "    IF    not $username_locator",
            "        RETURN    ${False}",
            "    END",
            "    ${is_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${username_locator}    timeout=3s",
            "    RETURN    ${is_visible}",
            "",
            "Perform Generated Login",
            "    ${username_locator}=    Get Variable Value    ${LOGIN_USERNAME_LOCATOR}    ${EMPTY}",
            "    ${password_locator}=    Get Variable Value    ${LOGIN_PASSWORD_LOCATOR}    ${EMPTY}",
            "    ${submit_locator}=    Get Variable Value    ${LOGIN_SUBMIT_LOCATOR}    ${EMPTY}",
            "    IF    $username_locator",
            "        Wait Until Element Is Visible    ${username_locator}    timeout=10s",
            "        Input Text    ${username_locator}    ${APP_USERNAME}",
            "    END",
            "    IF    $password_locator",
            "        Wait Until Element Is Visible    ${password_locator}    timeout=10s",
            "        Input Text    ${password_locator}    ${APP_PASSWORD}",
            "    END",
            "    IF    $submit_locator",
            "        Click Element    ${submit_locator}",
            "    END",
            "",
            "Use Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Get Variable Value    ${${locator_name}}    ${EMPTY}",
            "    Log    Using learned locator ${locator_name}: ${locator}",
            "    RETURN    ${locator}",
            "",
            "Click Using Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    IF    not $locator",
            "        Fail    Learned locator ${locator_name} is empty",
            "    END",
            "    Wait Until Element Is Visible    ${locator}    timeout=10s",
            "    Click Element    ${locator}",
            "",
            "Input Text Using Known Locator",
            "    [Arguments]    ${locator_name}    ${value}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    IF    not $locator",
            "        Fail    Learned locator ${locator_name} is empty",
            "    END",
            "    Wait Until Element Is Visible    ${locator}    timeout=10s",
            "    Input Text    ${locator}    ${value}",
            "",
            "Assert Element Using Known Locator",
            "    [Arguments]    ${locator_name}",
            "    ${locator}=    Use Known Locator    ${locator_name}",
            "    IF    not $locator",
            "        Fail    Learned locator ${locator_name} is empty",
            "    END",
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

        lines.extend([
            "Execute Generated Flow",
            "    [Arguments]    ${flow_name}",
            "    Run Keyword    ${flow_name}",
            "",
            "Execute Generated Page Action",
            "    [Arguments]    ${keyword_name}",
            "    Run Keyword    ${keyword_name}",
            "",
        ])

        for keyword_name, keyword_data in knowledge_index["action_keywords"].items():
            lines.extend(self._render_action_keyword(keyword_name, keyword_data))

        return "\n".join(lines).strip() + "\n"

    def _render_robot_test_case(self, test_case: Dict, knowledge_index: Dict) -> List[str]:
        title = self._robot_safe_name(test_case.get("title", "Generated Workflow"))
        tags = list(test_case.get("tags", []))
        scenario_type = test_case.get("scenario_type", "positive")
        scenario_category = test_case.get("scenario_category", "workflow")
        risk_level = test_case.get("risk_level", "medium")
        steps = test_case.get("steps", [])
        expected_results = test_case.get("expected_results", [])
        module_name = test_case.get("module_name", "")

        tags.extend([scenario_type, scenario_category, risk_level])
        tags = [tag for tag in dict.fromkeys(tags) if tag]

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
            rendered_step = self._render_structured_step(step, knowledge_index)
            if rendered_step:
                lines.extend(rendered_step)

        for expected in expected_results:
            safe_expected = expected.replace("${", "$\\{")
            lines.append(f"    Validate Generated Outcome    {safe_expected}")
        return lines

    def _write_page_resources(self, knowledge_index: Dict) -> List[str]:
        grouped_actions: Dict[str, List[Tuple[str, Dict]]] = {}
        for keyword_name, keyword_data in knowledge_index["action_keywords"].items():
            grouped_actions.setdefault(keyword_data["page_name"], []).append((keyword_name, keyword_data))

        for locator_name in knowledge_index["locators"].keys():
            page_name = self._page_name_from_locator_variable(locator_name)
            grouped_actions.setdefault(page_name, [])

        written_paths: List[str] = []
        for page_name, actions in grouped_actions.items():
            page_file = self.pages_dir / f"{self._slug(page_name)}_page.resource"
            open_keyword_name = self._robot_safe_name(f"Open {page_name} Page")
            visible_keyword_name = self._robot_safe_name(f"Verify {page_name} Page Is Visible")
            lines = [
                "*** Settings ***",
                "Documentation    AI-generated page resource for discovered page actions.",
                "Resource    ../generated_keywords.resource",
                "",
                "*** Keywords ***",
                open_keyword_name,
                "    Open Generated Workflow Start",
                f"    Log    Open page context for {page_name}",
                "",
                visible_keyword_name,
                "    Log    Verify page level content is visible",
            ]

            first_action = actions[0][1] if actions else {}
            first_locator = first_action.get("locator_variable", "")
            if first_locator:
                lines.append(f"    Assert Element Using Known Locator    {first_locator}")
            else:
                lines.append(f"    Perform Generated Step    Verify visible state for {page_name}")
            lines.append("")

            semantic_groups = self._group_actions_by_semantic_type(actions)
            lines.extend(self._render_page_semantic_keywords(page_name, semantic_groups))

            for keyword_name, keyword_data in actions:
                action_keyword_name = self._robot_safe_name(f"{page_name} Page {keyword_data['element_name']} Action")
                lines.extend(self._render_page_specific_action_keyword(action_keyword_name, keyword_data))
            page_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
            written_paths.append(page_file.as_posix())
        return written_paths

    def _write_flow_resources(self, test_cases: List[Dict], knowledge_index: Dict) -> List[str]:
        grouped_cases: Dict[str, List[Dict]] = {}
        for test_case in test_cases:
            flow_name = self._slug(test_case.get("workflow_type", "workflow"))
            grouped_cases.setdefault(flow_name, []).append(test_case)

        written_paths: List[str] = []
        for flow_name, cases in grouped_cases.items():
            flow_file = self.flows_dir / f"{flow_name}_flow.resource"
            lines = [
                "*** Settings ***",
                "Documentation    AI-generated flow resource for grouped workflow scenarios.",
                "Resource    ../generated_keywords.resource",
                "",
                "*** Keywords ***",
            ]
            for test_case in cases:
                flow_keyword_name = self._flow_keyword_name(test_case)
                lines.append(flow_keyword_name)
                lines.append("    Open Generated Workflow Start")
                mapped_keyword = self._select_keyword_for_test_case(test_case, knowledge_index)
                if mapped_keyword:
                    lines.append(f"    Execute Generated Page Action    {mapped_keyword}")
                page_open_keyword = self._page_open_keyword_for_test_case(test_case)
                if page_open_keyword:
                    lines.append(f"    {page_open_keyword}")
                for step in test_case.get("steps", []):
                    rendered_step = self._render_structured_step(step, knowledge_index)
                    if rendered_step:
                        lines.extend(rendered_step)
                page_visible_keyword = self._page_visible_keyword_for_test_case(test_case)
                if page_visible_keyword:
                    lines.append(f"    {page_visible_keyword}")
                for expected in test_case.get("expected_results", []):
                    safe_expected = expected.replace("${", "$\\{")
                    lines.append(f"    Validate Generated Outcome    {safe_expected}")
                lines.append("")
            flow_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
            written_paths.append(flow_file.as_posix())
        return written_paths

    def _write_modular_suites(self, test_cases: List[Dict], knowledge_index: Dict) -> List[str]:
        grouped_cases: Dict[str, List[Dict]] = {}
        for test_case in test_cases:
            suite_name = self._slug(test_case.get("scenario_category", "generated"))
            grouped_cases.setdefault(suite_name, []).append(test_case)

        written_paths: List[str] = []
        for suite_name, cases in grouped_cases.items():
            suite_file = self.suites_dir / f"{suite_name}.robot"
            lines = [
                "*** Settings ***",
                "Documentation    AI-generated modular Robot suite.",
                "Resource    ../generated_keywords.resource",
                f"Resource    ../flows/{self._slug(cases[0].get('workflow_type', 'workflow'))}_flow.resource",
                f"Resource    ../pages/{self._slug(cases[0].get('source_page', 'generated'))}_page.resource",
                "Suite Setup    Open Generated Application Session",
                "Suite Teardown    Close Generated Application Session",
                "Test Setup    Prepare Generated Test Context",
                "",
                "*** Test Cases ***",
            ]
            for test_case in cases:
                title = self._robot_safe_name(test_case.get("title", "Generated Workflow"))
                tags = list(dict.fromkeys([tag for tag in test_case.get("tags", []) if tag]))
                lines.append(title)
                if tags:
                    lines.append(f"    [Tags]    {'    '.join(tags)}")
                lines.append(f"    {self._flow_keyword_name(test_case)}")
                lines.append("")
            suite_file.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
            written_paths.append(suite_file.as_posix())
        return written_paths

    def _build_variable_content(self) -> str:
        framework_config = self.framework_config or self._load_framework_config()
        application = framework_config.get("application", {})
        authentication = framework_config.get("authentication", {})

        lines = [
            "*** Variables ***",
            f"${{APP_BASE_URL}}    {self._robot_scalar(application.get('base_url', ''))}",
            f"${{APP_LOGIN_URL}}    {self._robot_scalar(authentication.get('login_url', ''))}",
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
        lines.extend(self._render_action_body(keyword_data))
        lines.append(f"    Perform Generated Step    {keyword_data['description']}")
        lines.append("")
        return lines

    def _render_page_specific_action_keyword(self, keyword_name: str, keyword_data: Dict) -> List[str]:
        lines = [keyword_name]
        lines.append(f"    Log    Execute page-specific action for {keyword_data['element_name']} on {keyword_data['page_name']}")
        lines.extend(self._render_action_body(keyword_data))
        lines.append("")
        return lines

    def _group_actions_by_semantic_type(self, actions: List[Tuple[str, Dict]]) -> Dict[str, List[Dict]]:
        grouped: Dict[str, List[Dict]] = defaultdict(list)
        for _, keyword_data in actions:
            semantic_type = self._semantic_group_for_keyword(keyword_data)
            grouped[semantic_type].append(keyword_data)
        return grouped

    def _render_page_semantic_keywords(self, page_name: str, semantic_groups: Dict[str, List[Dict]]) -> List[str]:
        lines: List[str] = []

        if semantic_groups.get("authentication"):
            lines.extend(self._render_authentication_page_keywords(page_name, semantic_groups["authentication"]))
        if semantic_groups.get("search"):
            lines.extend(self._render_search_page_keywords(page_name, semantic_groups["search"]))
        if semantic_groups.get("form"):
            lines.extend(self._render_form_page_keywords(page_name, semantic_groups["form"]))
        if semantic_groups.get("action"):
            lines.extend(self._render_general_action_keywords(page_name, semantic_groups["action"]))
        if semantic_groups.get("assertion"):
            lines.extend(self._render_assertion_keywords(page_name, semantic_groups["assertion"]))

        return lines

    def _render_authentication_page_keywords(self, page_name: str, actions: List[Dict]) -> List[str]:
        username_action = self._pick_best_action(actions, ["user", "email", "login"])
        password_action = self._pick_best_action(actions, ["password", "pass"])
        submit_action = self._pick_best_action(actions, ["submit", "login", "sign in"])
        keyword_name = self._robot_safe_name(f"Login Through {page_name} Page")

        lines = [keyword_name]
        if username_action:
            lines.extend(self._render_action_body(username_action, override_value="AI_GENERATED_USER"))
        if password_action:
            lines.extend(self._render_action_body(password_action, override_value="AI_GENERATED_PASSWORD"))
        if submit_action:
            lines.extend(self._render_action_body(submit_action))
        if not any([username_action, password_action, submit_action]):
            lines.append(f"    Perform Generated Step    Login through {page_name}")
        lines.append("")
        return lines

    def _render_search_page_keywords(self, page_name: str, actions: List[Dict]) -> List[str]:
        input_action = self._pick_best_action(actions, ["search", "query", "term"])
        trigger_action = self._pick_best_action(actions, ["search", "submit", "go"])
        keyword_name = self._robot_safe_name(f"Search Through {page_name} Page")

        lines = [keyword_name]
        if input_action:
            lines.extend(self._render_action_body(input_action, override_value="AI_SEARCH_TERM"))
        if trigger_action and trigger_action != input_action:
            lines.extend(self._render_action_body(trigger_action))
        if not any([input_action, trigger_action]):
            lines.append(f"    Perform Generated Step    Execute search on {page_name}")
        lines.append("")
        return lines

    def _render_form_page_keywords(self, page_name: str, actions: List[Dict]) -> List[str]:
        fill_keyword = self._robot_safe_name(f"Populate {page_name} Form")
        submit_keyword = self._robot_safe_name(f"Submit {page_name} Form")
        cancel_keyword = self._robot_safe_name(f"Cancel {page_name} Form")

        lines = [fill_keyword]
        form_actions = [action for action in actions if self._keyword_action_strategy(action)[0] == "input"]
        if form_actions:
            for action in form_actions[:5]:
                lines.extend(self._render_action_body(action))
        else:
            lines.append(f"    Perform Generated Step    Populate form fields on {page_name}")
        lines.append("")

        submit_actions = [action for action in actions if any(term in action.get("element_name", "").lower() for term in ["save", "submit", "create", "update"])]
        lines.append(submit_keyword)
        if submit_actions:
            lines.extend(self._render_action_body(submit_actions[0]))
        else:
            lines.append(f"    Perform Generated Step    Submit form on {page_name}")
        lines.append("")

        cancel_actions = [action for action in actions if any(term in action.get("element_name", "").lower() for term in ["cancel", "close", "back"])]
        lines.append(cancel_keyword)
        if cancel_actions:
            lines.extend(self._render_action_body(cancel_actions[0]))
        else:
            lines.append(f"    Perform Generated Step    Cancel form on {page_name}")
        lines.append("")
        return lines

    def _render_general_action_keywords(self, page_name: str, actions: List[Dict]) -> List[str]:
        primary_action = self._pick_best_action(actions, ["submit", "save", "open", "select", "continue"])
        if not primary_action and actions:
            primary_action = actions[0]
        keyword_name = self._robot_safe_name(f"Execute Primary Action On {page_name} Page")
        lines = [keyword_name]
        if primary_action:
            lines.extend(self._render_action_body(primary_action))
        else:
            lines.append(f"    Perform Generated Step    Execute primary action on {page_name}")
        lines.append("")
        return lines

    def _render_assertion_keywords(self, page_name: str, actions: List[Dict]) -> List[str]:
        assertion_action = actions[0] if actions else None
        keyword_name = self._robot_safe_name(f"Verify Primary State On {page_name} Page")
        lines = [keyword_name]
        if assertion_action:
            lines.extend(self._render_action_body(assertion_action))
        else:
            lines.append(f"    Perform Generated Step    Verify primary state on {page_name}")
        lines.append("")
        return lines

    def _pick_best_action(self, actions: List[Dict], preferred_terms: List[str]) -> Dict | None:
        for term in preferred_terms:
            for action in actions:
                name = (action.get("element_name") or "").lower()
                if term in name:
                    return action
        return actions[0] if actions else None

    def _semantic_group_for_keyword(self, keyword_data: Dict) -> str:
        intent = (keyword_data.get("intent") or "").lower()
        element_name = (keyword_data.get("element_name") or "").lower()
        action_type, _ = self._keyword_action_strategy(keyword_data)

        if intent == "authentication" or any(term in element_name for term in ["user", "email", "password", "login", "sign in"]):
            return "authentication"
        if intent == "search" or "search" in element_name:
            return "search"
        if intent in {"data_entry", "data_submission", "edit"} or action_type == "input":
            return "form"
        if action_type == "assert":
            return "assertion"
        return "action"

    def _render_action_body(self, keyword_data: Dict, override_value: str = "") -> List[str]:
        lines: List[str] = []
        action_type, default_value = self._keyword_action_strategy(keyword_data)
        locator_variable = keyword_data.get("locator_variable")

        if action_type == "input":
            lines.append("    ${generated_value}=    Set Variable    AI_GENERATED_VALUE")
            effective_value = override_value or default_value
            if effective_value:
                lines.append(f"    ${'{'}generated_value{'}'}=    Set Variable    {effective_value}")
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
        return lines

    def _render_structured_step(self, step: str, knowledge_index: Dict) -> List[str]:
        safe_step = step.replace("${", "$\\{")
        lower_step = step.lower()
        matched_locator = self._match_locator_from_step(step, knowledge_index)

        if matched_locator and any(term in lower_step for term in ["enter", "input", "populate", "type", "leave"]):
            generated_value = self._default_value_from_step(lower_step)
            return [f"    Input Text Using Known Locator    {matched_locator}    {generated_value}"]

        if matched_locator and any(term in lower_step for term in ["click", "submit", "save", "execute", "use", "open", "select", "navigate", "attempt", "locate", "logout"]):
            return [f"    Click Using Known Locator    {matched_locator}"]

        if matched_locator and any(term in lower_step for term in ["verify", "observe", "display", "visible", "shown", "loaded", "disabled", "enabled", "interactable"]):
            return [f"    Assert Element Using Known Locator    {matched_locator}"]

        semantic_keyword = self._match_semantic_page_keyword(step, knowledge_index)
        if semantic_keyword:
            return [f"    {semantic_keyword}"]

        return [f"    Log    Unmapped generated step: {safe_step}"]

    def _match_locator_from_step(self, step: str, knowledge_index: Dict) -> str:
        lower_step = step.lower()
        scored_matches: List[Tuple[int, str]] = []
        for locator_name in knowledge_index["locators"].keys():
            normalized = locator_name.lower().replace("locator_", "").replace("_", " ")
            matched_tokens = [token for token in normalized.split() if token and token in lower_step]
            if matched_tokens:
                scored_matches.append((len(matched_tokens), locator_name))
        if not scored_matches:
            return ""
        scored_matches.sort(key=lambda item: item[0], reverse=True)
        return scored_matches[0][1]

    def _match_semantic_page_keyword(self, step: str, knowledge_index: Dict) -> str:
        lower_step = step.lower()
        if "login" in lower_step or ("username" in lower_step and "password" in lower_step):
            return "Perform Generated Login"
        if "search" in lower_step:
            return "Log    Execute semantic search action"
        if any(term in lower_step for term in ["page loads", "page is visible", "home page", "dashboard visible"]):
            visible_locator = self._pick_visible_assertion_locator(knowledge_index)
            if visible_locator:
                return f"Assert Element Using Known Locator    {visible_locator}"
        return ""

    def _default_value_from_step(self, lower_step: str) -> str:
        if "password" in lower_step:
            return "AI_GENERATED_PASSWORD"
        if "user" in lower_step or "email" in lower_step:
            return "AI_GENERATED_USER"
        if "search" in lower_step:
            return "AI_SEARCH_TERM"
        if "invalid" in lower_step:
            return "INVALID_VALUE"
        if "empty" in lower_step:
            return "${EMPTY}"
        if "maximum" in lower_step or "boundary" in lower_step:
            return "BOUNDARY_VALUE"
        return "AI_GENERATED_VALUE"

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

    def _pick_visible_assertion_locator(self, knowledge_index: Dict) -> str:
        preferred_terms = ["notifications", "coming_soon", "haklarr", "home"]
        locator_names = list(knowledge_index.get("locators", {}).keys())
        for term in preferred_terms:
            for locator_name in locator_names:
                if term in locator_name.lower():
                    return locator_name
        return locator_names[0] if locator_names else ""

    def _page_name_from_locator_variable(self, locator_name: str) -> str:
        raw = locator_name.replace("LOCATOR_", "", 1)
        if "_" not in raw:
            return raw or "generated"
        return raw.rsplit("_", 1)[0] or "generated"

    def _locator_variable_name(self, page_name: str, element_name: str) -> str:
        return f"LOCATOR_{self._slug(page_name)}_{self._slug(element_name)}"

    def _keyword_name(self, page_name: str, element_name: str, intent: str) -> str:
        return self._robot_safe_name(f"Perform {intent} on {element_name} in {page_name}")

    def _flow_keyword_name(self, test_case: Dict) -> str:
        workflow_type = test_case.get("workflow_type", "workflow")
        title = test_case.get("title", "generated workflow")
        return self._robot_safe_name(f"Execute {workflow_type} flow for {title}")

    def _page_open_keyword_for_test_case(self, test_case: Dict) -> str:
        source_page = test_case.get("source_page", "")
        if not source_page:
            return ""
        return self._robot_safe_name(f"Open {source_page} Page")

    def _page_visible_keyword_for_test_case(self, test_case: Dict) -> str:
        source_page = test_case.get("source_page", "")
        if not source_page:
            return ""
        return self._robot_safe_name(f"Verify {source_page} Page Is Visible")

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
