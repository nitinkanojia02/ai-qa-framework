*** Settings ***
Documentation    AI-generated Robot Framework suite from discovered application knowledge.
Resource    generated_keywords.resource
Suite Setup    Open Generated Application Session
Suite Teardown    Close Generated Application Session
Test Setup    Prepare Generated Test Context

*** Test Cases ***
Verify WashTAB Home Page Loads Successfully
    [Tags]    ai-generated    dashboard    home    page_load    smoke    ui    high
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Navigate to http://172.21.166.115/washtabui/home
    Log    Unmapped generated step: Observe the page header and dashboard area
    Log    Unmapped generated step: Verify the presence of the home icon, notifications icon, and user chip displaying 'haklarr'
    Log    Unmapped generated step: Verify that multiple dashboard tiles (innerBtn elements) are displayed
    Verify washtab Page Is Visible
    Verify washtab Page Is Visible
    Validate Generated Outcome    Header icons such as home, notifications, and arrow back are visible
    Validate Generated Outcome    User chip displaying 'haklarr' is visible
    Validate Generated Outcome    Dashboard tiles are displayed and appear clickable

Verify Logout from User Chip
    [Tags]    ai-generated    authentication    header    home    logout    workflow    high
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate the user chip displaying 'haklarr' in the header
    Log    Unmapped generated step: Click the log-out icon inside the user chip
    Verify washtab Page Is Visible
    Validate Generated Outcome    Logout action is triggered
    Validate Generated Outcome    User session is terminated
    Verify washtab Page Is Visible

Verify Notifications Button Disabled State
    [Tags]    ai-generated    disabled    home    notifications    ui_state_validation    ui_validation    validation    medium
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate the notifications button with id 'notifications-button'
    Log    Unmapped generated step: Observe that the button has aria-disabled set to true
    Log    Unmapped generated step: Attempt to click the notifications button
    Verify washtab Page Is Visible
    Validate Generated Outcome    Notifications button appears visually disabled
    Validate Generated Outcome    Clicking the button does not trigger any action or navigation

Verify Home Icon Presence and Interaction
    [Tags]    ai-generated    header    home    home_icon    navigation    positive    action    medium
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate the icon with name 'home' in the header
    Log    Unmapped generated step: Click the home icon
    Verify washtab Page Is Visible
    Validate Generated Outcome    Home icon is visible in the header
    Validate Generated Outcome    Clicking the home icon keeps the user on or navigates to the home dashboard

Verify Arrow Back Icon Behavior
    [Tags]    ai-generated    back    header    home    navigation    navigation_back    workflow    medium
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate the icon with name 'arrow-back'
    Log    Unmapped generated step: Click the arrow back icon
    Verify washtab Page Is Visible
    Validate Generated Outcome    Arrow back icon is visible in the header
    Validate Generated Outcome    Clicking the icon navigates to the previous page in the session history

Verify Dashboard Tile Interaction
    [Tags]    ai-generated    dashboard    dashboard_navigation    home    navigation    positive    tiles    action    medium
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate one of the dashboard tiles with class 'innerBtn'
    Log    Unmapped generated step: Click the tile
    Verify washtab Page Is Visible
    Validate Generated Outcome    Tile responds to user interaction
    Validate Generated Outcome    Associated action or navigation is triggered for the selected tile

Verify Coming Soon Tile is Non-Functional
    [Tags]    ai-generated    coming_soon    edge    feature_placeholder    home    placeholder    ui_validation    validation    low
    Open washtab Page
    Log    Navigate within module: home
    Log    Unmapped generated step: Locate the tile displaying text 'Coming Soon!'
    Log    Unmapped generated step: Attempt to click the 'Coming Soon!' tile
    Verify washtab Page Is Visible
    Validate Generated Outcome    The 'Coming Soon!' label is visible
    Validate Generated Outcome    Clicking the tile does not navigate to a new page or trigger an active workflow
