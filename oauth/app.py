from flask import Flask, redirect, request
import os
import secrets
import urllib.parse

app = Flask(__name__)

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
REDIRECT_URI = os.environ.get("TIKTOK_REDIRECT_URI", "")

@app.route("/")
def home():
    return """
    <h1>RondappsClipper</h1>
    <p>OAuth Server aktif.</p>
    <a href="/auth/tiktok">Hubungkan TikTok</a>
    """

@app.route("/auth/tiktok")
def tiktok_login():
    if not CLIENT_KEY or not REDIRECT_URI:
        return "TIKTOK_CLIENT_KEY atau TIKTOK_REDIRECT_URI belum dikonfigurasi.", 500

    state = secrets.token_urlsafe(32)

    params = {
        "client_key": CLIENT_KEY,
        "response_type": "code",
        "scope": "user.info.basic",
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }

    url = (
        "https://www.tiktok.com/v2/auth/authorize/?"
        + urllib.parse.urlencode(params)
    )

    response = redirect(url)
    response.set_cookie(
        "oauth_state",
        state,
        max_age=600,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return response


@app.route("/auth/callback")
def callback():
    error = request.args.get("error")

    if error:
        return f"""
        <h2>Login TikTok gagal</h2>
        <p>{error}</p>
        <p>{request.args.get("error_description", "")}</p>
        """

    code = request.args.get("code")
    state = request.args.get("state")

    saved_state = request.cookies.get("oauth_state")

    if not code:
        return "Authorization code tidak ditemukan.", 400

    if not state or state != saved_state:
        return "State tidak cocok. OAuth request ditolak.", 400

    return """
    <h2>Berhasil!</h2>
    <p>TikTok mengembalikan authorization code.</p>
    <p>Server OAuth RondappsClipper sudah menerima callback.</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
