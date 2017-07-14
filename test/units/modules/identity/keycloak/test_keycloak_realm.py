import collections
import os
import unittest

from ansible.modules.identity.keycloak.keycloak_realm import *


class KeycloakRealmTestCase(unittest.TestCase):
 
    def test_create_realm(self):
        toCreate = dict(
            realm='test',
            url='http://localhost:18081',
            username='admin',
            password='admin',
            name='test',
            namehtml='ceci est un test',
            accessCodeLifespan=60,
            accessCodeLifespanLogin=1800,
            accessCodeLifespanUserAction=300,
            notBefore = 0,
            revokeRefreshToken = False,
            accessTokenLifespan = 300,
            accessTokenLifespanForImplicitFlow = 900,
            ssoSessionIdleTimeout = 1800,
            ssoSessionMaxLifespan = 36000,
            offlineSessionIdleTimeout = 2592000,
            enabled = True,
            sslRequired = "external",
            registrationAllowed = False,
            registrationEmailAsUsername = False,
            rememberMe = False,
            verifyEmail = False,
            loginWithEmailAllowed = True,
            duplicateEmailsAllowed = False,
            resetPasswordAllowed = False,
            editUsernameAllowed = False,
            bruteForceProtected = False,
            maxFailureWaitSeconds = 900,
            minimumQuickLoginWaitSeconds = 60,
            waitIncrementSeconds = 60,
            quickLoginCheckMilliSeconds = 1000,
            maxDeltaTimeSeconds = 43200,
            failureFactor = 30,
            defaultRoles = [ "offline_access", "uma_authorization" ],
            requiredCredentials = [ "password" ],
            passwordPolicy = "hashIterations(20000)",
            otpPolicyType = "totp",
            otpPolicyAlgorithm = "HmacSHA1",
            otpPolicyInitialCounter = 0,
            otpPolicyDigits = 6,
            otpPolicyLookAheadWindow = 1,
            otpPolicyPeriod = 30,
            smtpServer = dict(
                replyToDisplayName = 'root',
                starttls = "",
                auth = "",
                port = "25",
                host = "localhost",
                replyTo = "root@localhost",
                fromDisplayName = "local",
                envelopeFrom = "root@localhost",
                ssl = ""),
            eventsEnabled = False,
            eventsListeners = [ "jboss-logging" ],
            enabledEventTypes = [],
            adminEventsEnabled= False,
            adminEventsDetailsEnabled = False,
            internationalizationEnabled = False,
            supportedLocales= [ ],
            browserFlow= "browser",
            registrationFlow= "registration",
            directGrantFlow= "direct grant",
            resetCredentialsFlow= "reset credentials",
            clientAuthenticationFlow= "clients",
            state='present',
            force=False,
            attributes=None,
            browserSecurityHeaders=None
        )        
        toCreate['smtpServer']['from'] = 'root@localhost'
    
        results = realm(toCreate)
        self.assertTrue(results['ansible_facts']['realm']['enabled'])
        
    def test_modify_realm(self):
        toModifiy = dict(
            realm='test',
            url='http://localhost:18081',
            username='admin',
            password='admin',
            name='test123',
            namehtml='ceci est un test',
            accessCodeLifespan=60,
            accessCodeLifespanLogin=1800,
            accessCodeLifespanUserAction=300,
            notBefore = 0,
            revokeRefreshToken = False,
            accessTokenLifespan = 300,
            accessTokenLifespanForImplicitFlow = 900,
            ssoSessionIdleTimeout = 1800,
            ssoSessionMaxLifespan = 36000,
            offlineSessionIdleTimeout = 2592000,
            enabled = True,
            sslRequired = "external",
            registrationAllowed = False,
            registrationEmailAsUsername = False,
            rememberMe = False,
            verifyEmail = False,
            loginWithEmailAllowed = True,
            duplicateEmailsAllowed = False,
            resetPasswordAllowed = False,
            editUsernameAllowed = False,
            bruteForceProtected = False,
            maxFailureWaitSeconds = 900,
            minimumQuickLoginWaitSeconds = 60,
            waitIncrementSeconds = 60,
            quickLoginCheckMilliSeconds = 1000,
            maxDeltaTimeSeconds = 43200,
            failureFactor = 30,
            defaultRoles = [ "offline_access", "uma_authorization" ],
            requiredCredentials = [ "password" ],
            passwordPolicy = "hashIterations(20000)",
            otpPolicyType = "totp",
            otpPolicyAlgorithm = "HmacSHA1",
            otpPolicyInitialCounter = 0,
            otpPolicyDigits = 6,
            otpPolicyLookAheadWindow = 1,
            otpPolicyPeriod = 30,
            smtpServer = dict(
                replyToDisplayName = 'root',
                starttls = "",
                auth = "",
                port = "25",
                host = "localhost",
                replyTo = "root@localhost",
                fromDisplayName = "local",
                envelopeFrom = "root@localhost",
                ssl = ""),
            eventsEnabled = False,
            eventsListeners = [ "jboss-logging" ],
            enabledEventTypes = [],
            adminEventsEnabled= False,
            adminEventsDetailsEnabled = False,
            internationalizationEnabled = False,
            supportedLocales= [ ],
            browserFlow= "browser",
            registrationFlow= "registration",
            directGrantFlow= "direct grant",
            resetCredentialsFlow= "reset credentials",
            clientAuthenticationFlow= "clients",
            state='present',
            force=False,
            attributes=None,
            browserSecurityHeaders=None
        )        
        toModifiy['smtpServer']['from'] = 'root@localhost'
        results = realm(toModifiy)
        
        self.assertEqual(results['ansible_facts']['realm']['displayName'], 'test123', 'name has changed')
        
    def test_delete_realm(self):
        toDelete = dict(
            realm='test',
            url='http://localhost:18081',
            username='admin',
            password='admin',
            name='test123',
            namehtml='ceci est un test',
            accessCodeLifespan=60,
            accessCodeLifespanLogin=1800,
            accessCodeLifespanUserAction=300,
            notBefore = 0,
            revokeRefreshToken = False,
            accessTokenLifespan = 300,
            accessTokenLifespanForImplicitFlow = 900,
            ssoSessionIdleTimeout = 1800,
            ssoSessionMaxLifespan = 36000,
            offlineSessionIdleTimeout = 2592000,
            enabled = True,
            sslRequired = "external",
            registrationAllowed = False,
            registrationEmailAsUsername = False,
            rememberMe = False,
            verifyEmail = False,
            loginWithEmailAllowed = True,
            duplicateEmailsAllowed = False,
            resetPasswordAllowed = False,
            editUsernameAllowed = False,
            bruteForceProtected = False,
            maxFailureWaitSeconds = 900,
            minimumQuickLoginWaitSeconds = 60,
            waitIncrementSeconds = 60,
            quickLoginCheckMilliSeconds = 1000,
            maxDeltaTimeSeconds = 43200,
            failureFactor = 30,
            defaultRoles = [ "offline_access", "uma_authorization" ],
            requiredCredentials = [ "password" ],
            passwordPolicy = "hashIterations(20000)",
            otpPolicyType = "totp",
            otpPolicyAlgorithm = "HmacSHA1",
            otpPolicyInitialCounter = 0,
            otpPolicyDigits = 6,
            otpPolicyLookAheadWindow = 1,
            otpPolicyPeriod = 30,
            smtpServer = dict(
                replyToDisplayName = 'root',
                starttls = "",
                auth = "",
                port = "25",
                host = "localhost",
                replyTo = "root@localhost",
                fromDisplayName = "local",
                envelopeFrom = "root@localhost",
                ssl = ""),
            eventsEnabled = False,
            eventsListeners = [ "jboss-logging" ],
            enabledEventTypes = [],
            adminEventsEnabled= False,
            adminEventsDetailsEnabled = False,
            internationalizationEnabled = False,
            supportedLocales= [ ],
            browserFlow= "browser",
            registrationFlow= "registration",
            directGrantFlow= "direct grant",
            resetCredentialsFlow= "reset credentials",
            clientAuthenticationFlow= "clients",
            state='absent',
            force=False,
            attributes=None,
            browserSecurityHeaders=None
        )        
        toDelete['smtpServer']['from'] = 'root@localhost'
        results = realm(toDelete)
        self.assertEqual(results['stdout'], 'deleted', 'realm has been deleted')
