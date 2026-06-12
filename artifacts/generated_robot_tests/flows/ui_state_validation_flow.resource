*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute ui state validation flow for Verify Notifications Button Disabled State
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Locate the notifications button with id 'notifications-button'
    Log    Unmapped generated step: Observe that the button has aria-disabled set to true
    Log    Unmapped generated step: Attempt to click the notifications button
    Verify washtab Page Is Visible
    Validate Generated Outcome    Notifications button appears visually disabled
    Validate Generated Outcome    Clicking the button does not trigger any action or navigation
