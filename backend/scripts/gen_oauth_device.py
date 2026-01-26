import json
import os
import time
import webbrowser
from datetime import datetime, timezone

import requests

SCOPE = "https://www.googleapis.com/auth/youtube"
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

def main():
    client_id = os.getenv("YTMUSIC_CLIENT_ID") or input("Client ID: ").strip()
    client_secret = os.getenv("YTMUSIC_CLIENT_SECRET") or input("Client Secret: ").strip()
    out_path = os.getenv("YTMUSIC_OAUTH_PATH", "backend/data/oauth.json")

    # 1) Get device code
    r = requests.post(
        DEVICE_CODE_URL,
        data={"client_id": client_id, "scope": SCOPE},
        timeout=30,
    )
    r.raise_for_status()
    code_data = r.json()

    user_code = code_data["user_code"]
    verification_url = code_data.get("verification_url") or code_data.get("verification_uri")
    verification_url_complete = code_data.get("verification_url_complete") or code_data.get("verification_uri_complete")
    device_code = code_data["device_code"]
    interval = int(code_data.get("interval", 5))
    expires_in = int(code_data.get("expires_in", 1800))
    deadline = time.time() + expires_in

    print("\n1) Abrí esta URL y pegá el código:")
    print("   URL:", verification_url_complete or verification_url)
    print("   Código:", user_code)

    try:
        webbrowser.open(verification_url_complete or verification_url)
    except Exception:
        pass

    # 2) Poll token endpoint
    print("\n2) Esperando autorización en Google (polling)...")
    sleep_s = interval

    while time.time() < deadline:
        tr = requests.post(
            TOKEN_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            timeout=30,
        )
        data = tr.json()

        if "access_token" in data:
            # Success
            access_token = data["access_token"]
            refresh_token = data.get("refresh_token")
            token_type = data.get("token_type", "Bearer")
            expires_in_tok = int(data.get("expires_in", 3600))
            scope = data.get("scope", SCOPE)

            if not refresh_token:
                print("\n⚠️ No vino refresh_token.")
                print("Esto suele pasar si ya autorizaste antes. Revocá el acceso de la app y repetí.")
                print("Google Account -> Security -> Third-party access -> Remove access.")
                # Igual guardamos lo que hay, pero te va a expirar.
            payload = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": now_ts() + expires_in_tok,
                "token_type": token_type,
                "scope": scope,
            }

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            print(f"\n✅ Listo. Generado: {out_path}")
            return

        err = data.get("error")
        if err in ("authorization_pending",):
            time.sleep(sleep_s)
            continue
        if err in ("slow_down",):
            sleep_s += 5
            time.sleep(sleep_s)
            continue
        if err in ("access_denied", "expired_token"):
            raise SystemExit(f"\n❌ OAuth falló: {data}")

        # Otro error
        raise SystemExit(f"\n❌ OAuth falló: {data}")

    raise SystemExit("\n❌ Timeout esperando autorización (expiró el device_code).")

if __name__ == "__main__":
    main()
