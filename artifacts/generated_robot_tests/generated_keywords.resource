*** Settings ***
Documentation    Generated keyword and locator resource from application knowledge.
Library    BuiltIn
Library    SeleniumLibrary
Resource    generated_variables.resource

*** Variables ***

*** Keywords ***
Open Generated Application Session
    ${browser}=    Get Variable Value    ${BROWSER}    chrome
    ${start_url}=    Get Variable Value    ${APP_BASE_URL}    ${EMPTY}
    Open Browser    ${start_url}    ${browser}
    Maximize Browser Window
    ${login_needed}=    Is Generated Login Required
    IF    $login_needed and $APP_USERNAME and $APP_PASSWORD
        ${login_url}=    Get Variable Value    ${APP_LOGIN_URL}    ${EMPTY}
        IF    $login_url
            Go To    ${login_url}
        END
        Perform Generated Login
    END

Close Generated Application Session
    Close All Browsers

Prepare Generated Test Context
    Log    Prepare generated test context for execution

Open Generated Workflow Start
    Go To    ${APP_BASE_URL}

Is Generated Login Required
    ${username_locator}=    Get Variable Value    ${LOGIN_USERNAME_LOCATOR}    ${EMPTY}
    IF    not $username_locator
        RETURN    ${False}
    END
    ${is_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${username_locator}    timeout=3s
    RETURN    ${is_visible}

Perform Generated Login
    ${username_locator}=    Get Variable Value    ${LOGIN_USERNAME_LOCATOR}    ${EMPTY}
    ${password_locator}=    Get Variable Value    ${LOGIN_PASSWORD_LOCATOR}    ${EMPTY}
    ${submit_locator}=    Get Variable Value    ${LOGIN_SUBMIT_LOCATOR}    ${EMPTY}
    IF    $username_locator
        Wait Until Element Is Visible    ${username_locator}    timeout=10s
        Input Text    ${username_locator}    ${APP_USERNAME}
    END
    IF    $password_locator
        Wait Until Element Is Visible    ${password_locator}    timeout=10s
        Input Text    ${password_locator}    ${APP_PASSWORD}
    END
    IF    $submit_locator
        Click Element    ${submit_locator}
    END

Use Known Locator
    [Arguments]    ${locator_name}
    ${locator}=    Get Variable Value    ${${locator_name}}    ${EMPTY}
    Log    Using learned locator ${locator_name}: ${locator}
    RETURN    ${locator}

Click Using Known Locator
    [Arguments]    ${locator_name}
    ${locator}=    Use Known Locator    ${locator_name}
    IF    not $locator
        Fail    Learned locator ${locator_name} is empty
    END
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Click Element    ${locator}

Input Text Using Known Locator
    [Arguments]    ${locator_name}    ${value}
    ${locator}=    Use Known Locator    ${locator_name}
    IF    not $locator
        Fail    Learned locator ${locator_name} is empty
    END
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Input Text    ${locator}    ${value}

Assert Element Using Known Locator
    [Arguments]    ${locator_name}
    ${locator}=    Use Known Locator    ${locator_name}
    IF    not $locator
        Fail    Learned locator ${locator_name} is empty
    END
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Element Should Be Visible    ${locator}

Perform Generated Step
    [Arguments]    ${step}
    Log    Execute generated step: ${step}

Validate Generated Outcome
    [Arguments]    ${expected}
    Log    Validate generated outcome: ${expected}

Execute Generated Flow
    [Arguments]    ${flow_name}
    Run Keyword    ${flow_name}

Execute Generated Page Action
    [Arguments]    ${keyword_name}
    Run Keyword    ${keyword_name}
