#!/usr/bin/env python3
"""Interactive, no-persistence handoff from a human to the kit's Cursor client.

The URL may be supplied as an argument. The bridge token is *only* accepted
through a hidden terminal prompt, never from argv, a prompt, or a repo file.
"""

import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys
import warnings
from urllib.parse import urlsplit

CLIENT = Path(__file__).resolve().parents[1] / "client.py"
BRIDGE_PATH = "/v1/enrich-user-story"


def validate_url(value: str) -> str:
    value = value.strip()
    try:
        parsed = urlsplit(value)
        port = parsed.port  # Reject malformed ports before launching the client.
    except ValueError as exc:
        raise ValueError("URL HTTPS inválida") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != BRIDGE_PATH
        or parsed.query
        or parsed.fragment
        or any(ch.isspace() for ch in value)
        or port == 0
    ):
        raise ValueError(f"Se requiere https://DOMINIO{BRIDGE_PATH} sin credenciales ni parámetros")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Invocar el cliente Hermes–Cursor sin guardar ni mostrar el token"
    )
    parser.add_argument("request", help="JSON de solicitud (por ejemplo, examples/request.json)")
    parser.add_argument("--out", required=True, help="Salida nueva; no se sobrescribe")
    parser.add_argument("--url", help="URL HTTPS completa; si se omite, se pregunta")
    args = parser.parse_args(argv)
    try:
        url = validate_url(args.url if args.url is not None else input("URL HTTPS del bridge: "))
    except (ValueError, EOFError) as exc:
        print(f"Onboarding: {exc}", file=sys.stderr)
        return 2
    if not sys.stdin.isatty():
        print("Onboarding: introduce el token solo en una terminal interactiva; no en Cursor Chat.", file=sys.stderr)
        return 2
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            token = getpass.getpass("Token del bridge (entrada oculta): ").strip()
    except getpass.GetPassWarning:
        print("Onboarding: no hay entrada oculta disponible; usa una terminal local.", file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\nOnboarding cancelado.", file=sys.stderr)
        return 2
    if not token or any(ch.isspace() for ch in token):
        print("Onboarding: token vacío o inválido.", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["HERMES_BRIDGE_URL"] = url
    env["HERMES_BRIDGE_TOKEN"] = token
    try:
        result = subprocess.run(
            [sys.executable, str(CLIENT), args.request, "--out", args.out],
            env=env,
            check=False,
        )
    except OSError:
        print("Onboarding: no se pudo ejecutar el cliente.", file=sys.stderr)
        return 1
    finally:
        env.pop("HERMES_BRIDGE_TOKEN", None)
        token = ""
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
