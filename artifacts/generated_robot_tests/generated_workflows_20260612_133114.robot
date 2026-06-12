*** Settings ***
Documentation    AI-generated Robot Framework suite from discovered application knowledge.
Resource    generated_keywords.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify WashTAB home page loads successfully
    [Tags]    ai-generated    dashboard    home    page_load    smoke    high
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Open the WashTAB home URL in the browser
    Perform Generated Step    Observe the header and dashboard area
    Perform Generated Step    Verify presence of the home icon, notifications button, and user chip displaying 'haklarr'
    Perform Generated Step    Verify multiple dashboard tile buttons are displayed
    Validate Generated Outcome    WashTAB home page loads without errors
    Validate Generated Outcome    Home icon is visible in the header
    Validate Generated Outcome    User chip displaying 'haklarr' is visible
    Validate Generated Outcome    Dashboard tile buttons are displayed on the page

Verify user logout from header
    [Tags]    ai-generated    authentication    header    home    logout    workflow    high
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Locate the user chip labeled 'haklarr'
    Perform Generated Step    Click the log-out icon inside the user chip
    Validate Generated Outcome    Logout action is triggered
    Validate Generated Outcome    User session ends and user is logged out of the application

Verify notifications button is disabled
    [Tags]    ai-generated    disabled_state    home    negative    notification_access    notifications    ui    action    medium
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Locate the notifications button with id 'notifications-button'
    Perform Generated Step    Observe its state
    Perform Generated Step    Attempt to click the notifications button
    Validate Generated Outcome    Notifications button appears disabled
    Validate Generated Outcome    Clicking the disabled notifications button does not trigger any action

Verify navigation using back arrow icon
    [Tags]    ai-generated    back    header    home    navigation    workflow    medium
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Locate the arrow-back icon
    Perform Generated Step    Click the arrow-back icon
    Validate Generated Outcome    Application performs a navigation action to the previous or parent screen

Verify dashboard tile buttons respond to user interaction
    [Tags]    ai-generated    dashboard    home    module_access    positive    tile    action    medium
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Locate any dashboard tile with class 'innerBtn'
    Perform Generated Step    Click the tile button
    Validate Generated Outcome    Tile responds to the click interaction
    Validate Generated Outcome    Application triggers the corresponding module action or navigation

Verify 'Coming Soon!' tile is not active
    [Tags]    ai-generated    coming_soon    dashboard    disabled_feature    feature_availability    home    validation    low
    Open Generated Workflow Start
    Perform Generated Step    Navigate within module: home
    Perform Generated Step    Locate the tile displaying text 'Coming Soon!'
    Perform Generated Step    Attempt to click the tile
    Validate Generated Outcome    Tile displays the text 'Coming Soon!'
    Validate Generated Outcome    Tile does not navigate or trigger any functional workflow
