*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute navigation flow for Verify navigation using back arrow icon
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Locate the arrow-back icon
    Perform Generated Step    Click the arrow-back icon
    Verify washtab Page Is Visible
    Validate Generated Outcome    Application performs a navigation action to the previous or parent screen
