*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute logout flow for Verify Logout from User Chip
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Locate the user chip displaying 'haklarr' in the header
    Log    Unmapped generated step: Click the log-out icon inside the user chip
    Verify washtab Page Is Visible
    Validate Generated Outcome    Logout action is triggered
    Validate Generated Outcome    User session is terminated
    Validate Generated Outcome    User is redirected away from the authenticated home page
