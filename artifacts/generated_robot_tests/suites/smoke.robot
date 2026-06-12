*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/page_load_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify WashTAB Home Page Loads Successfully
    [Tags]    ai-generated    dashboard    home    page_load    smoke    ui
    Execute page load flow for Verify WashTAB Home Page Loads Successfully
