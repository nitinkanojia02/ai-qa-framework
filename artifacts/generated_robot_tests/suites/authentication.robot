*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/logout_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify Logout from User Chip
    [Tags]    ai-generated    authentication    header    home    logout    workflow
    Execute logout flow for Verify Logout from User Chip
