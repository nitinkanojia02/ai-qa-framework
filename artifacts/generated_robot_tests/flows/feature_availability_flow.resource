*** Settings ***
Documentation    AI-generated flow resource for grouped workflow scenarios.
Resource    ../generated_keywords.resource

*** Keywords ***
Execute feature availability flow for Verify 'Coming Soon!' tile is not active
    Open Generated Workflow Start
    Open washtab Page
    Perform Generated Step    Locate the tile displaying text 'Coming Soon!'
    Perform Generated Step    Attempt to click the tile
    Verify washtab Page Is Visible
    Validate Generated Outcome    Tile displays the text 'Coming Soon!'
    Validate Generated Outcome    Tile does not navigate or trigger any functional workflow
