*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute dashboard navigation flow for Verify Dashboard Tile Interaction
    Open Generated Workflow Start
    Open washtab Page
    Log    Unmapped generated step: Locate one of the dashboard tiles with class 'innerBtn'
    Log    Unmapped generated step: Click the tile
    Verify washtab Page Is Visible
    Validate Generated Outcome    Tile responds to user interaction
    Validate Generated Outcome    Associated action or navigation is triggered for the selected tile
