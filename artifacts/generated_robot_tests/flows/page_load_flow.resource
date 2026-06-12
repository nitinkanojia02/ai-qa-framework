*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute page load flow for Verify WashTAB home page loads successfully
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Open the WashTAB home URL in the browser
    Perform Generated Step    Observe the header and dashboard area
    Perform Generated Step    Verify presence of the home icon, notifications button, and user chip displaying 'haklarr'
    Perform Generated Step    Verify multiple dashboard tile buttons are displayed
    Verify washtab Page Is Visible
    Validate Generated Outcome    WashTAB home page loads without errors
    Validate Generated Outcome    Home icon is visible in the header
    Validate Generated Outcome    User chip displaying 'haklarr' is visible
    Validate Generated Outcome    Dashboard tile buttons are displayed on the page
