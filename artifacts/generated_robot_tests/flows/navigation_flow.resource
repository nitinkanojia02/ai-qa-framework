*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute navigation flow for Verify Home Icon Presence and Interaction
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Locate the icon with name 'home' in the header
    Log    Unmapped generated step: Click the home icon
    Verify washtab Page Is Visible
    Validate Generated Outcome    Home icon is visible in the header
    Validate Generated Outcome    Clicking the home icon keeps the user on or navigates to the home dashboard
