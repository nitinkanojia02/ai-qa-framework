# Generated Manual Test Cases

## AUTO-MTC-001 - Verify WashTAB Home Page Loads Successfully

**Objective:** Ensure the WashTAB home dashboard loads with key UI elements visible.
**Workflow Type:** page_load
**Scenario Type:** smoke
**Scenario Category:** smoke
**Risk Level:** high
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, dashboard, home, page_load, smoke, ui

### Preconditions
- User has access to the WashTAB application URL
- User session is active and user is logged in

### Steps
1. Navigate to http://172.21.166.115/washtabui/home
2. Observe the page header and dashboard area
3. Verify the presence of the home icon, notifications icon, and user chip displaying 'haklarr'
4. Verify that multiple dashboard tiles (innerBtn elements) are displayed

### Expected Results
- WashTAB home page loads successfully without errors
- Header icons such as home, notifications, and arrow back are visible
- User chip displaying 'haklarr' is visible
- Dashboard tiles are displayed and appear clickable

## AUTO-MTC-002 - Verify Logout from User Chip

**Objective:** Confirm that the user can log out using the logout icon in the user chip.
**Workflow Type:** logout
**Scenario Type:** workflow
**Scenario Category:** authentication
**Risk Level:** high
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, authentication, header, home, logout, workflow

### Preconditions
- User is logged into the WashTAB application
- Home page is displayed
- User chip showing 'haklarr' is visible

### Steps
1. Locate the user chip displaying 'haklarr' in the header
2. Click the log-out icon inside the user chip

### Expected Results
- Logout action is triggered
- User session is terminated
- User is redirected away from the authenticated home page

## AUTO-MTC-003 - Verify Notifications Button Disabled State

**Objective:** Ensure the notifications button is disabled and not clickable when aria-disabled is true.
**Workflow Type:** ui_state_validation
**Scenario Type:** validation
**Scenario Category:** validation
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, disabled, home, notifications, ui_state_validation, ui_validation, validation

### Preconditions
- User is logged in
- WashTAB home page is open

### Steps
1. Locate the notifications button with id 'notifications-button'
2. Observe that the button has aria-disabled set to true
3. Attempt to click the notifications button

### Expected Results
- Notifications button appears visually disabled
- Clicking the button does not trigger any action or navigation

## AUTO-MTC-004 - Verify Home Icon Presence and Interaction

**Objective:** Validate that the home icon is visible and functions as a navigation control.
**Workflow Type:** navigation
**Scenario Type:** positive
**Scenario Category:** action
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, header, home, home_icon, navigation, positive

### Preconditions
- User is logged in
- WashTAB home page is loaded

### Steps
1. Locate the icon with name 'home' in the header
2. Click the home icon

### Expected Results
- Home icon is visible in the header
- Clicking the home icon keeps the user on or navigates to the home dashboard

## AUTO-MTC-005 - Verify Arrow Back Icon Behavior

**Objective:** Confirm that the arrow back icon functions as a back navigation control.
**Workflow Type:** navigation_back
**Scenario Type:** workflow
**Scenario Category:** workflow
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, back, header, home, navigation, navigation_back, workflow

### Preconditions
- User is logged in
- User previously navigated from another page to the WashTAB home page

### Steps
1. Locate the icon with name 'arrow-back'
2. Click the arrow back icon

### Expected Results
- Arrow back icon is visible in the header
- Clicking the icon navigates to the previous page in the session history

## AUTO-MTC-006 - Verify Dashboard Tile Interaction

**Objective:** Ensure dashboard tiles represented by innerBtn elements respond to user interaction.
**Workflow Type:** dashboard_navigation
**Scenario Type:** positive
**Scenario Category:** action
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, dashboard, dashboard_navigation, home, navigation, positive, tiles

### Preconditions
- User is logged in
- WashTAB home page is loaded

### Steps
1. Locate one of the dashboard tiles with class 'innerBtn'
2. Click the tile

### Expected Results
- Tile responds to user interaction
- Associated action or navigation is triggered for the selected tile

## AUTO-MTC-007 - Verify Coming Soon Tile is Non-Functional

**Objective:** Ensure the 'Coming Soon!' tile indicates unavailable functionality and does not trigger navigation.
**Workflow Type:** feature_placeholder
**Scenario Type:** edge
**Scenario Category:** validation
**Risk Level:** low
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, coming_soon, edge, feature_placeholder, home, placeholder, ui_validation

### Preconditions
- User is logged in
- WashTAB home page is displayed

### Steps
1. Locate the tile displaying text 'Coming Soon!'
2. Attempt to click the 'Coming Soon!' tile

### Expected Results
- The 'Coming Soon!' label is visible
- Clicking the tile does not navigate to a new page or trigger an active workflow
