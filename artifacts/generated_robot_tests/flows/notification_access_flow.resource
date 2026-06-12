*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute notification access flow for Verify notifications button is disabled
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Locate the notifications button with id 'notifications-button'
    Perform Generated Step    Observe its state
    Perform Generated Step    Attempt to click the notifications button
    Verify washtab Page Is Visible
    Validate Generated Outcome    Notifications button appears disabled
    Validate Generated Outcome    Clicking the disabled notifications button does not trigger any action
