*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/navigation_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify navigation using back arrow icon
    [Tags]    ai-generated    back    header    home    navigation    workflow
    Execute navigation flow for Verify navigation using back arrow icon
