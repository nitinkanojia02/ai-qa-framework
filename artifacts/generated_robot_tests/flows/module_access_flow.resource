*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute module access flow for Verify dashboard tile buttons respond to user interaction
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Locate any dashboard tile with class 'innerBtn'
    Perform Generated Step    Click the tile button
    Verify washtab Page Is Visible
    Validate Generated Outcome    Tile responds to the click interaction
    Validate Generated Outcome    Application triggers the corresponding module action or navigation
