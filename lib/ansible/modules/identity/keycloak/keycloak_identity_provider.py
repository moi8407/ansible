#!/usr/bin/python
# -*- coding: utf-8 -*-
from pip._vendor.requests.models import Request
from curses.ascii import NUL

# (c) 2017, Philippe Gauthier INSPQ <philippe.gauthier@inspq.qc.ca>
#
# This file is not part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
author: "Philippe Gauthier (philippe.gauthier@inspq.qc.ca"
module: keycloak_identity_provider
short_description: Configure an identity provider in Keycloak
description:
  - This module creates, removes or update Keycloak identity provider.
version_added: "1.1"
options:
  url:
    description:
    - str: The url of the Keycloak server.
    default: http://localhost:8080/auth
    required: true    
  username:
    description:
    - str: The username to logon to the master realm.
    required: true
  password:
    description:
    - str: The password for the user to logon the master realm.
    required: true
  realm:
    description:
    - str: The name of the realm in which is the identity provider.
    required: true
  alias:
    description:
    - str: The alias of the identity provider.
    required: true
  displayName:
    description:
    - str: The display name of the realm.
    required: false
  providerId:
    description:
    - str: Type of identity provider.
    default: oidc
    required: false
  enabled
    description:
    - bool : enabled.
    default: True
    required: false
  updateProfileFirstLoginMode:
    description:
    - str: update Profile First Login Mode.
    default: on
    required: false
  trustEmail:
    description: 
    - bool : trust Email.
    default: False
    required: false
  storeToken:
    description:
    - bool : store Token.
    default: True
    required: false
  addReadTokenRoleOnCreate:
    description:
    - bool : add Read Token Role On Create.
    default: True
    required: false
  authenticateByDefault:
    description:
    - bool : authenticate By Default.
    default: False
    required: false
  linkOnly
    description:
    - bool : link Only.
    default: False
    required: false
  firstBrokerLoginFlowAlias
    description:
    - str : first Broker Login Flow Alias.
    default: first broker login
    required: false
  hideOnLoginPage
    description:
    - bool : hide On Login Page. 
    default: False
    required: false
  openIdConfigurationUrl
    description:
    - str : OpenId Connect configuration auto discovery URL.
    default: 
    required: true
  validateSignature
    description:
    - bool : validate Signature.
    default: True
    required: false
  clientId
    description:
    - str : clientId.
    default:
    required: true
  backchannelSupported
    description:
    - bool : backchannelSupported.
    default: False
    required: false
  useJwksUrl
    description:
    - bool : use Jwks Url.
    default: True
    required: false
  disableUserInfo
    description:
    - bool : disable User Info (must be true for ADFS).
    default: False
    required: false
  clientSecret
    description:
    - str : client Secret.
    default:
    required: true
  defaultScope
    description:
    - str : default Scope.
    default: ""
    required: false
  state:
    choices: [ "present", "absent" ]
    default: present
    description:
    - Control if the realm exists.
    required: false
  force:
    choices: [ "yes", "no" ]
    default: "no"
    description:
    - If yes, allows to remove realm and recreate it.
    required: false
notes:
  - module does not modify identity provider alias.
'''

EXAMPLES = '''
# Create a realm realm1 with default settings.
- keycloak_identity_provider:
    alias: alias1
    state: present

# Re-create the realm realm1
- keycloak_identity_provider:
    alias: alias1
    state: present
    force: yes

# Remove a the realm realm1.
- keycloak_identity_provider:
    alias: alias1
    state: absent
'''

RETURN = '''
result:
    ansible_facts: Representation JSON du fournisseur d'identité
    stderr: Message d'erreur s'il y en a un
    rc: Code de retour, 0 si succès, 1 si erreur
    changed: Retourne vrai si l'action a modifié le fournisseur d'identité, faux sinon.
'''
import requests
import json
import urllib
from ansible.module_utils.keycloak_utils import isDictEquals

def login(url, username, password):
    '''
Fonction : login
Description :
    Cette fonction permet de s'authentifier sur le serveur Keycloak.
Arguments :
    url :
        type : str
        description :
            url de base du serveur Keycloak        
    username :
        type : str
        description :
            identifiant à utiliser pour s'authentifier au serveur Keycloak        
    password :
        type : str
        description :
            Mot de passe pour s'authentifier au serveur Keycloak        
    '''
    # Login to Keycloak
    accessToken = ""
    body = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': 'admin-cli'
    }
    try:
        loginResponse = requests.post(url + '/auth/realms/master/protocol/openid-connect/token',data=body)
    
        loginData = loginResponse.json()
        accessToken = loginData['access_token']
    except requests.exceptions.RequestException, e:
        raise e
    except ValueError, e:
        raise e

    return accessToken

    
def addIdPEndpoints(idPConfiguration):
    '''
fonction :      addIdPEndpoints
description:    Cette fonction permet d'intéroger le endpoint openid-configuration d'un fournisseur
                d'identité afin d'en extraire les différents endpoints à mettre dans l'objet
                config de keycloak.
paramètres:
    idPConfiguration:
    type: dict
    description: Dictionnaire contenant ls structure config à compléter qui inclus le endpoint
                 openid-configuration à interroger dans la clé openIdConfigurationUrl
    '''
    url = None
    if 'openIdConfigurationUrl' in idPConfiguration.keys():
        url = idPConfiguration["openIdConfigurationUrl"]
        del idPConfiguration["openIdConfigurationUrl"]
    if url is not None:
        try:
            openidConfigRequest = requests.get(url, verify=False)
            openIdConfig = openidConfigRequest.json()
            if 'userinfo_endpoint' in openIdConfig.keys():
                idPConfiguration["userInfoUrl"] = openIdConfig["userinfo_endpoint"]
            if 'token_endpoint' in openIdConfig.keys():
                idPConfiguration["tokenUrl"] = openIdConfig["token_endpoint"]
            if 'jwks_uri' in openIdConfig.keys():
                idPConfiguration["jwksUrl"] = openIdConfig["jwks_uri"]
            if 'issuer' in openIdConfig.keys():
                idPConfiguration["issuer"] = openIdConfig["issuer"]
            if 'authorization_endpoint' in openIdConfig.keys():
                idPConfiguration["authorizationUrl"] = openIdConfig["authorization_endpoint"]
            if 'end_session_endpoint' in openIdConfig.keys():
                idPConfiguration["logoutUrl"] = openIdConfig["end_session_endpoint"]        
        except Exception, e:
            raise e
def deleteAllMappers(url, bearerHeader):
    changed = False
    try:
        # Obtenir la liste des mappers existant
        getMappersRequest = requests.get(url + '/mappers', headers={'Authorization' : bearerHeader})
        mappers = getMappersRequest.json()
        for mapper in mappers:
            requests.delete(url + '/mappers/' + mapper['id'], headers={'Authorization' : bearerHeader})
    except requests.exceptions.RequestException, ValueError:
        return False
    except Exception, e:
        raise e
     
    return changed
def createOrUpdateMappers(url, bearerHeader, alias, idPMappers):
    changed = False
    create = False
   
    try:
        # Obtenir la liste des mappers existant
        getMappersRequest = requests.get(url + '/mappers', headers={'Authorization' : bearerHeader})
        try:
            mappers = getMappersRequest.json()
        except ValueError: # Il n'y a pas de mapper de défini pour cet IdP
            mappers = []
            create = True
        for idPMapper in idPMappers:
            mapperFound = False
            mapperId = ""
            for mapper in mappers:
                if mapper['name'] == idPMapper['name']:
                    mapperId = mapper['id']
        
            if len(mapperId) == 0:
                mapper = {}
                
            for key in idPMapper: 
                mapperChanged = False
                if key in mapper.keys():
                    if type(idPMapper[key]) is dict:
                        for dictKey in idPMapper[key]:
                            if dictKey not in mapper[key].keys() or idPMapper[key][dictKey] <> mapper[key][dictKey]:
                                mapper[key][dictKey] = idPMapper[key][dictKey]
                                mapperChanged = True
                    elif idPMapper[key] <> mapper[key]:      
                        mapper[key] = idPMapper[key]
                        mapperChanged = True
                else:
                    mapper[key] = idPMapper[key]
                    mapperChanged = True
            if 'identityProviderMapper' in idPMapper.keys(): # si le type de mapper a été fourni
                if mapper['identityProviderMapper'] <> idPMapper['identityProviderMapper']:
                    mapper['identityProviderMapper'] = idPMapper['identityProviderMapper']
                    mapperChanged = True
            else: # Sinon, utiliser la valeur par défaut
                if 'identityProviderMapper' not in mapper.keys():
                    mapper['identityProviderMapper'] = 'oidc-user-attribute-idp-mapper'
                    mapperChanged = True
            if 'identityProviderAlias' not in mapper.keys() or mapper['identityProviderAlias'] <> alias:
                mapper['identityProviderAlias'] = alias
                mapperChanged = True
            if mapperChanged:
                data=json.dumps(mapper)
                #print str(data)
                if len(mapperId) == 0:
                    response = requests.post(url + '/mappers', headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'}, data=data)
                else:
                    response = requests.put(url + '/mappers/' + mapperId, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'}, data=data)
                changed = True 
    except Exception ,e :
        raise e
    return changed

def main():
    module = AnsibleModule(
        argument_spec = dict(
            url=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(required=True),
            realm=dict(type='str', required=True),
            alias=dict(type='str', required=True),
            displayName=dict(type='str', default=""),
            providerId=dict(type='str', default="oidc"),
            enabled = dict(type='bool', default=True),
            updateProfileFirstLoginMode=dict(type='str', default="on"),
            trustEmail=dict(type='bool',default=False),
            storeToken = dict(type='bool',default=True),
            addReadTokenRoleOnCreate = dict(type='bool', default=True),
            authenticateByDefault = dict(type='bool', default=False),
            linkOnly = dict(type='bool', default=False),
            firstBrokerLoginFlowAlias = dict(type='str', default="first broker login"),
            config = dict(type='dict', required=True),
            mappers = dict(type='list', default=[]),
            state=dict(choices=["absent", "present"], default='present'),
            force=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    params = module.params.copy()
    params['force'] = module.boolean(module.params['force'])
    
    result = idp(params)
    
    if result['rc'] != 0:
        module.fail_json(msg='non-zero return code', **result)
    else:
        module.exit_json(**result)
    
    
def idp(params):
    url = params['url']
    username = params['username']
    password = params['password']
    realm = params['realm']
    state = params['state']
    force = params['force']

    # Créer un représentation du realm recu en paramètres
    newIdPRepresentation = {}
    newIdPRepresentation["alias"] = params['alias'].decode("utf-8")
    newIdPRepresentation["displayName"] = params['displayName'].decode("utf-8")
    newIdPRepresentation["providerId"] = params['providerId'].decode("utf-8")
    newIdPRepresentation["enabled"] = params['enabled']
    newIdPRepresentation["updateProfileFirstLoginMode"] = params['updateProfileFirstLoginMode'].decode("utf-8")
    newIdPRepresentation["trustEmail"] = params['trustEmail']
    newIdPRepresentation["storeToken"] = params['storeToken']
    newIdPRepresentation["addReadTokenRoleOnCreate"] = params['addReadTokenRoleOnCreate']
    newIdPRepresentation["authenticateByDefault"] = params['authenticateByDefault']
    newIdPRepresentation["linkOnly"] = params['linkOnly']
    newIdPRepresentation["firstBrokerLoginFlowAlias"] = params['firstBrokerLoginFlowAlias'].decode("utf-8")
    newIdPConfig = params['config']
    newIdPMappers = params['mappers']
    
    # Compléter la configuration reçu avec les valeurs par défaut
    if 'hideOnLoginPage' not in newIdPConfig.keys():
        newIdPConfig["hideOnLoginPage"] = "false"
    if 'validateSignature' not in newIdPConfig.keys():
        newIdPConfig["validateSignature"] = "true"
    if 'validateSignature' not in newIdPConfig.keys():
        newIdPConfig["backchannelSupported"] = "false"
    if 'useJwksUrl' not in newIdPConfig.keys():
        newIdPConfig["useJwksUrl"] = "true"
    if 'disableUserInfo' not in newIdPConfig.keys():
        newIdPConfig["disableUserInfo"] = "false"
    if 'defaultScope' not in newIdPConfig.keys():
        newIdPConfig["defaultScope"] = ""
    if newIdPRepresentation["providerId"] == 'google':
        if 'userIp' not in newIdPConfig.keys():
            newIdPConfig["userIp"] = "false"
    
    try:
        addIdPEndpoints(newIdPConfig)
        newIdPRepresentation["config"] = newIdPConfig
    except Exception, e:
        result = dict(
            stderr   = 'addIdPEndpoints: ' + str(e),
            rc       = 1,
            changed  = changed
            )
        return result

    idPSvcBaseUrl = url + "/auth/admin/realms/" + realm + "/identity-provider/instances/"
    idPSvcUrl = idPSvcBaseUrl + newIdPRepresentation["alias"]
    rc = 0
    result = dict()
    changed = False

    try:
        accessToken = login(url, username, password)
        bearerHeader = "bearer " + accessToken
    except Exception, e:
        result = dict(
            stderr   = 'login: ' + str(e),
            rc       = 1,
            changed  = changed
            )
        return result
    try: 
        # Vérifier si le IdP existe sur le serveur Keycloak
        getResponse = requests.get(idPSvcUrl, headers={'Authorization' : bearerHeader})
    except requests.HTTPError, e:
        getStatusCode = getResponse.status_code
    except:
        getStatusCode = 0
    else:
        getStatusCode = getResponse.status_code
        
    
   
    if (getStatusCode == 404): # Le IdP n'existe pas
        # Creer le IdP
        
        if (state == 'present'): # Si le status est présent
            try:
                # Stocker le IdP dans un body prêt a être posté
                data=json.dumps(newIdPRepresentation)
                # Créer le IdP
                postResponse = requests.post(idPSvcBaseUrl, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'}, data=data)
                # S'il y a des mappers de définis pour l'IdP
                if len(newIdPMappers) > 0:
                    if createOrUpdateMappers(idPSvcUrl, bearerHeader, newIdPRepresentation["alias"], newIdPMappers):
                        changed = True
                # Obtenir le nouvel IdP créé
                getResponse = requests.get(idPSvcUrl, headers={'Authorization' : bearerHeader})
                idPRepresentation = getResponse.json()
                
                getResponse = requests.get(idPSvcUrl + "/mappers", headers={'Authorization' : bearerHeader})
                try:
                    mappersRepresentation = getResponse.json()
                except ValueError:
                    mappersRepresentation = {}
                changed = True
                fact = dict(
                    idp = idPRepresentation,
                    mappers = mappersRepresentation)
                result = dict(
                    ansible_facts = fact,
                    rc = 0,
                    changed = changed
                    )
            except requests.exceptions.RequestException, e:
                fact = dict(
                    idp = newIdPRepresentation)
                result = dict(
                    ansible_facts= fact,
                    stderr   = 'post idp: ' + newIdPRepresentation["alias"] + ' erreur: ' + str(e),
                    rc       = 1,
                    changed  = changed
                    )
            except ValueError, e:
                fact = dict(
                    idp = newIdPRepresentation)
                result = dict(
                    ansible_facts = fact,
                    stderr   = 'post idp: ' + newIdPRepresentation["alias"] + ' erreur: ' + str(e),
                    rc       = 1,
                    changed  = changed
                    )
        else: # Sinon, le status est absent
            result = dict(
                stdout   = newIdPRepresentation["alias"] + ' absent',
                rc       = 0,
                changed  = changed
            )
                
    elif (getStatusCode == 200):  # Le realm existe déjà
        try:
            if (state == 'present'): # si le status est présent
                # Obtenir le IdP exitant
                idPRepresentation = getResponse.json()
                if force: # Si l'option force est sélectionné
                    alias = newIdPRepresentation['alias']
                    # Supprimer les mappings existants
                    deleteAllMappers(idPSvcUrl, bearerHeader)
                    # Supprimer le IdP existant
                    deleteResponse = requests.delete(idPSvcUrl, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'})
                    changed = True
                    # Stocker le IdP dans un body prêt a être posté
                    data=json.dumps(newIdPRepresentation)
                    # Créer le nouveau IdP
                    postResponse = requests.post(idPSvcBaseUrl, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'}, data=data)
                else: # Si l'option force n'est pas sélectionné
                    # Comparer les realms
                    if (isDictEquals(newIdPRepresentation, idPRepresentation, ["clientSecret", "openIdConfigurationUrl", "mappers"])): # Si le nouveau IdP n'introduit pas de modification au IdP existant
                        # Ne rien changer
                        changed = False
                    else: # Si le IdP doit être modifié
                        # Enlever le champ alias avec de faire le put
                        alias = newIdPRepresentation.pop('alias')
                        
                        # Stocker le IdP dans un body prêt a être posté
                        data=json.dumps(newIdPRepresentation)
                        # Mettre à jour le IdP sur le serveur Keycloak
                        updateResponse = requests.put(idPSvcUrl, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'}, data=data)
                        changed = True
                if changed and len(newIdPMappers) > 0:
                    createOrUpdateMappers(idPSvcUrl, bearerHeader, alias, newIdPMappers)
        
                # Obtenir sa représentation JSON sur le serveur Keycloak                        
                getResponse = requests.get(idPSvcUrl, headers={'Authorization' : bearerHeader})
                idPRepresentation = getResponse.json()
                
                getResponse = requests.get(idPSvcUrl + "/mappers", headers={'Authorization' : bearerHeader})
                try:
                    mappersRepresentation = getResponse.json()
                except ValueError:
                    mappersRepresentation = {}
                
                fact = dict(
                    idp = idPRepresentation,
                    mappers = mappersRepresentation)
                result = dict(
                    ansible_facts = fact,
                    rc = 0,
                    changed = changed
                    )
                    
            else: # Le status est absent
                # Supprimer le IdP
                deleteResponse = requests.delete(idPSvcUrl, headers={'Authorization' : bearerHeader, 'Content-type': 'application/json'})
                changed = True
                result = dict(
                    stdout   = 'deleted',
                    rc       = 0,
                    changed  = changed
                )
        except requests.exceptions.RequestException, e:
            result = dict(
                stderr   = 'put or delete idp: ' + newRealmRepresentation["id"] + ' error: ' + str(e),
                rc       = 1,
                changed  = changed
                )
        except ValueError, e:
            result = dict(
                stderr   = 'put or delete idp: ' + newRealmRepresentation["id"] + ' error: ' + str(e),
                rc       = 1,
                changed  = changed
                )
    else: # Le status HTTP du GET n'est ni 200 ni 404, c'est considéré comme une erreur.
        rc = 1
        result = dict(
            stderr = newRealmRepresentation["id"] + ' ' + getStatusCode,
            rc = 1,
            changed = changed
            )

    return result
        
# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
