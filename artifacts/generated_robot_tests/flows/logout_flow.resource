*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute logout flow for Verify user logout from header
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Locate the user chip labeled 'haklarr'
    Perform Generated Step    Click the log-out icon inside the user chip
    Verify washtab Page Is Visible
    Validate Generated Outcome    Logout action is triggered
    Validate Generated Outcome    User session ends and user is logged out of the application
