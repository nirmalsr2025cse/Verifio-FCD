from authlib.integrations.flask_client import OAuth
from utils.config import appConf

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register("google",
        client_id = appConf.get("GOOGLE_CLIENT_ID"),
        client_secret = appConf.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url = appConf.get("GOOGLE_META_URL"),
        client_kwargs = {
            "scope": "openid email profile"
        }
    )

    oauth.register(name='microsoft',
        client_id=appConf.get("MICROSOFT_CLIENT_ID"),
        client_secret=appConf.get("MICROSOFT_CLIENT_SECRET"),
        server_metadata_url=appConf.get("MICROSOFT_META_URL"),
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    oauth.register(name='github',
        client_id=appConf.get("GITHUB_CLIENT_ID"),
        client_secret=appConf.get("GITHUB_CLIENT_SECRET"),
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/',
        client_kwargs={
            "scope": "user:email"
        }
    )

    oauth.register(
        name='discord',
        client_id=appConf.get("DISCORD_CLIENT_ID"),
        client_secret=appConf.get("DISCORD_CLIENT_SECRET"),
        authorize_url='https://discord.com/api/oauth2/authorize',
        access_token_url='https://discord.com/api/oauth2/token',
        api_base_url='https://discord.com/api/',
        client_kwargs={
            "scope": "identify email"
        }
    )
