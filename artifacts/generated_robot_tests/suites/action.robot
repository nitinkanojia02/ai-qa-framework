*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/navigation_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify Home Icon Presence and Interaction
    [Tags]    ai-generated    header    home    home_icon    navigation    positive
    Execute navigation flow for Verify Home Icon Presence and Interaction

Verify Dashboard Tile Interaction
    [Tags]    ai-generated    dashboard    dashboard_navigation    home    navigation    positive    tiles
    Execute dashboard navigation flow for Verify Dashboard Tile Interaction
