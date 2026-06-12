# Generated Manual Test Cases

## AUTO-MTC-001 - Verify WashTAB home page loads successfully

**Objective:** Ensure the WashTAB home dashboard loads and key UI elements are visible.
**Workflow Type:** page_load
**Scenario Type:** smoke
**Scenario Category:** smoke
**Risk Level:** high
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, dashboard, home, page_load, smoke

### Preconditions
- User has access to the WashTAB application
- User navigates to http://172.21.166.115/washtabui/home

### Steps
1. Open the WashTAB home URL in the browser
2. Observe the header and dashboard area
3. Verify presence of the home icon, notifications button, and user chip displaying 'haklarr'
4. Verify multiple dashboard tile buttons are displayed

### Expected Results
- WashTAB home page loads without errors
- Home icon is visible in the header
- User chip displaying 'haklarr' is visible
- Dashboard tile buttons are displayed on the page

## AUTO-MTC-002 - Verify user logout from header

**Objective:** Ensure a logged-in user can initiate logout using the logout icon.
**Workflow Type:** logout
**Scenario Type:** workflow
**Scenario Category:** authentication
**Risk Level:** high
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, authentication, header, home, logout, workflow

### Preconditions
- User is logged into WashTAB
- Home page is displayed
- User chip 'haklarr' and log-out icon are visible

### Steps
1. Locate the user chip labeled 'haklarr'
2. Click the log-out icon inside the user chip

### Expected Results
- Logout action is triggered
- User session ends and user is logged out of the application

## AUTO-MTC-003 - Verify notifications button is disabled

**Objective:** Confirm that the notifications button cannot be interacted with when disabled.
**Workflow Type:** notification_access
**Scenario Type:** negative
**Scenario Category:** action
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, disabled_state, home, negative, notification_access, notifications, ui

### Preconditions
- User is on the WashTAB home page

### Steps
1. Locate the notifications button with id 'notifications-button'
2. Observe its state
3. Attempt to click the notifications button

### Expected Results
- Notifications button appears disabled
- Clicking the disabled notifications button does not trigger any action

## AUTO-MTC-004 - Verify navigation using back arrow icon

**Objective:** Ensure the arrow-back icon performs a navigation action when selected.
**Workflow Type:** navigation
**Scenario Type:** workflow
**Scenario Category:** workflow
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, back, header, home, navigation, workflow

### Preconditions
- User is on the WashTAB home page
- Arrow-back icon is visible in the header

### Steps
1. Locate the arrow-back icon
2. Click the arrow-back icon

### Expected Results
- Application performs a navigation action to the previous or parent screen

## AUTO-MTC-005 - Verify dashboard tile buttons respond to user interaction

**Objective:** Ensure dashboard tiles are interactive and respond to user clicks.
**Workflow Type:** module_access
**Scenario Type:** positive
**Scenario Category:** action
**Risk Level:** medium
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, dashboard, home, module_access, positive, tile

### Preconditions
- User is logged into WashTAB
- Home dashboard is displayed

### Steps
1. Locate any dashboard tile with class 'innerBtn'
2. Click the tile button

### Expected Results
- Tile responds to the click interaction
- Application triggers the corresponding module action or navigation

## AUTO-MTC-006 - Verify 'Coming Soon!' tile is not active

**Objective:** Ensure the 'Coming Soon!' tile indicates unavailable functionality and does not perform actions.
**Workflow Type:** feature_availability
**Scenario Type:** validation
**Scenario Category:** validation
**Risk Level:** low
**Module:** home
**Primary Entity:** home
**Tags:** ai-generated, coming_soon, dashboard, disabled_feature, feature_availability, home, validation

### Preconditions
- User is on the WashTAB home page

### Steps
1. Locate the tile displaying text 'Coming Soon!'
2. Attempt to click the tile

### Expected Results
- Tile displays the text 'Coming Soon!'
- Tile does not navigate or trigger any functional workflow
