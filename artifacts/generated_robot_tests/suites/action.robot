*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/notification_access_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify notifications button is disabled
    [Tags]    ai-generated    disabled_state    home    negative    notification_access    notifications    ui
    Execute notification access flow for Verify notifications button is disabled

Verify dashboard tile buttons respond to user interaction
    [Tags]    ai-generated    dashboard    home    module_access    positive    tile
    Execute module access flow for Verify dashboard tile buttons respond to user interaction
