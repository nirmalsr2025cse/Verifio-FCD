from flask import Blueprint , redirect , url_for , session
from utils.oauth import oauth
from utils.db import FCD_collection
import secrets

oauth_bp = Blueprint('oauth',__name__)

@oauth_bp.route('/google-login')
def google_login():
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce

    return oauth.google.authorize_redirect(
        redirect_uri=url_for('oauth.google_callback', _external=True),
        nonce=nonce
    )


@oauth_bp.route('/signin-google')
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(
        token,
        nonce=session.get('nonce')
    )

    email = userinfo.get('email')
    name = userinfo.get("name", "")

    parts = name.split()

    first_name = parts[0] if len(parts) > 0 else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    session['user'] = email

    existing_user = FCD_collection.find_one({'email': email})

    if not existing_user:
        FCD_collection.insert_one({
            'FirstName': first_name,
            'LastName':last_name,
            'email': email,
            'password': None,
            'auth_type': 'google'
        })

    return redirect(url_for('dashboard.home'))

@oauth_bp.route('/microsoft-login')
def microsoft_login():
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce

    return oauth.microsoft.authorize_redirect(
        redirect_uri=url_for('oauth.microsoft_callback', _external=True),
        nonce=nonce
    )

@oauth_bp.route('/signin-microsoft')
def microsoft_callback():
    token = oauth.microsoft.authorize_access_token()

    userinfo = oauth.microsoft.parse_id_token(
        token,
        nonce=session.get('nonce')
    )

    email = userinfo.get('preferred_username')
    name = userinfo.get("name", "")

    parts = name.split()

    first_name = parts[0] if len(parts) > 0 else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    session['user'] = email

    existing_user = FCD_collection.find_one({'email': email})

    if not existing_user:
        FCD_collection.insert_one({
            'FirstName': first_name,
            'LastName':last_name,
            'email': email,
            'password': None,
            'auth_type': 'microsoft'
        })

    return redirect(url_for('dashboard.home'))

@oauth_bp.route('/github-login')
def github_login():
    return oauth.github.authorize_redirect(
        redirect_uri=url_for('oauth.github_callback', _external=True)
    )

@oauth_bp.route('/signin-github')
def github_callback():
    token = oauth.github.authorize_access_token()

    resp = oauth.github.get('user')
    user_info = resp.json()

    email = user_info.get('email')

    if not email:
        emails = oauth.github.get('user/emails').json()
        email = emails[0]['email']

    name = user_info.get('name') or user_info.get('login')

    parts = name.split()

    first_name = parts[0] if len(parts) > 0 else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    session['user'] = email

    existing_user = FCD_collection.find_one({'email': email})

    if not existing_user:
        FCD_collection.insert_one({
            'FirstName': first_name,
            'LastName':last_name,
            'email': email,
            'password': None,
            'auth_type': 'github'
        })

    return redirect(url_for('dashboard.home'))

@oauth_bp.route('/discord-login')
def discord_login():
    return oauth.discord.authorize_redirect(
        redirect_uri=url_for('oauth.discord_callback', _external=True)
    )

@oauth_bp.route('/signin-discord')
def discord_callback():
    token = oauth.discord.authorize_access_token()

    user = oauth.discord.get('users/@me').json()

    email = user.get('email')
    name = user.get('username')
    parts = name.split()

    first_name = parts[0] if len(parts) > 0 else ""
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    session['user'] = email

    existing_user = FCD_collection.find_one({'email': email})

    if not existing_user:
        FCD_collection.insert_one({
            'FirstName': first_name,
            'LastName':last_name,
            'email': email,
            'password': None,
            'auth_type': 'discord'
        })

    return redirect(url_for('dashboard.home'))