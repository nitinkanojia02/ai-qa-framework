*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute navigation back flow for Verify Arrow Back Icon Behavior
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Locate the icon with name 'arrow-back'
    Log    Unmapped generated step: Click the arrow back icon
    Verify washtab Page Is Visible
    Validate Generated Outcome    Arrow back icon is visible in the header
    Validate Generated Outcome    Clicking the icon navigates to the previous page in the session history
