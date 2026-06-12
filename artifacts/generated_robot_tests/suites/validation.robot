*** Settings ***
Documentation    AI-generated modular Robot suite.
Resource    ../generated_keywords.resource
Resource    ../flows/feature_availability_flow.resource
Resource    ../pages/washtab_page.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify 'Coming Soon!' tile is not active
    [Tags]    ai-generated    coming_soon    dashboard    disabled_feature    feature_availability    home    validation
    Execute feature availability flow for Verify 'Coming Soon!' tile is not active
