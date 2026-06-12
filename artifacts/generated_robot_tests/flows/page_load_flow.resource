*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute page load flow for Verify WashTAB Home Page Loads Successfully
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Navigate to http://172.21.166.115/washtabui/home
    Log    Unmapped generated step: Observe the page header and dashboard area
    Log    Unmapped generated step: Verify the presence of the home icon, notifications icon, and user chip displaying 'haklarr'
    Log    Unmapped generated step: Verify that multiple dashboard tiles (innerBtn elements) are displayed
    Verify washtab Page Is Visible
    Validate Generated Outcome    WashTAB home page loads successfully without errors
    Validate Generated Outcome    Header icons such as home, notifications, and arrow back are visible
    Validate Generated Outcome    User chip displaying 'haklarr' is visible
    Validate Generated Outcome    Dashboard tiles are displayed and appear clickable
