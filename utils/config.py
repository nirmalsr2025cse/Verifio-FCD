import os

appConf = {
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
    "GOOGLE_META_URL": "https://accounts.google.com/.well-known/openid-configuration",

    "MICROSOFT_CLIENT_ID": os.getenv("MICROSOFT_CLIENT_ID"),
    "MICROSOFT_CLIENT_SECRET": os.getenv("MICROSOFT_CLIENT_SECRET"),
    "MICROSOFT_META_URL": "https://login.microsoftonline.com/db759d2f-b372-4ba7-ab8a-1277af94f4d1/v2.0/.well-known/openid-configuration",

    "GITHUB_CLIENT_ID": os.getenv("GITHUB_CLIENT_ID"),
    "GITHUB_CLIENT_SECRET": os.getenv("GITHUB_CLIENT_SECRET"),

    "DISCORD_CLIENT_ID": os.getenv("DISCORD_CLIENT_ID"),
    "DISCORD_CLIENT_SECRET": os.getenv("DISCORD_CLIENT_SECRET"),

    "FLASK_SECRET": os.getenv("FLASK_SECRET"),
    "FLASK_PORT": 5000
}