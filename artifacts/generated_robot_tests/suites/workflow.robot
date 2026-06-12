*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/navigation_back_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify Arrow Back Icon Behavior
    [Tags]    ai-generated    back    header    home    navigation    navigation_back    workflow
    Execute navigation back flow for Verify Arrow Back Icon Behavior
