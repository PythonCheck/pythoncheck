# -*- coding: utf-8 -*-
from gluon.custom_import import track_changes; track_changes(True)
from gluon.contrib.login_methods.ldap_auth import ldap_auth

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

def process_login_accept(f):
    user_has_membership = db(db.auth_membership.user_id == auth.user_id)
    if user_has_membership.count() < 1:
        import re
        group_id = 1 if re.compile('^\d+$').match(f.vars['username']) else 2
        db.auth_membership.insert(user_id=auth.user_id,
                                  group_id=group_id)
    print f.vars;

# all we need is login
auth.settings.actions_disabled=['register','change_password','request_reset_password','retrieve_username']

# you don't have to remember me
auth.settings.remember_me_form = False

auth.settings.login_methods = [ldap_auth(mode='ad',
   server='deepspace.htlw3r.ac.at',
   # server='localhost',
   base_dn='dc=htlw3r,dc=ac,dc=at',
   manage_user=True,
   user_firstname_attrib='givenName',
   user_lastname_attrib='sn',
   db=db)]

auth.settings.login_onaccept = (process_login_accept)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.logged_url = URL(c='default', f='index') # if accessing register or similar as logged in user redirect to the me page
auth.settings.login_next = URL(c='default', f='index') 
auth.settings.controller = 'user'
auth.settings.register_next = URL(c='default', f='index')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = False
auth.settings.register_onaccept = (lambda f: auth.add_membership(1, auth.user_id))

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

@auth.requires_login()
def requires_role(role):
    def decorator(fn):
        def f():
            hasRole = has_role(role)
            if hasRole is None:
                redirect(URL(request.application, 'user', 'login?_next=' + request.env.path_info))
            elif hasRole == True:
                return fn()
            else:
                redirect(URL(request.application, 'user', 'not_authorized'))
        return f
    return decorator

def has_role(role):
    if hasattr(auth.user_groups, 'values') and len(auth.user_groups.values()) > 0:
        roleId = db(db.auth_group.role.like(role.lower())).select()
        if roleId:
            roleId = roleId[0].id
            for group_key in auth.user_groups.keys():
                if group_key >= roleId:
                    return True
            else:
                return False
        else:
            return False
    return None