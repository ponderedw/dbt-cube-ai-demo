#!/usr/bin/env python3
"""
Superset database connection setup — creates the Cube SQL connection only.
Datasets are synced separately by dbt-cube-sync cube-to-bi.
"""
import os
import socket
import requests
import time
import sys


def wait_for_port(host, port, max_retries=60, delay=5):
    for attempt in range(max_retries):
        try:
            with socket.create_connection((host, port), timeout=3):
                print(f"✓ {host}:{port} is ready")
                return True
        except (OSError, ConnectionRefusedError):
            print(f"⏳ Waiting for {host}:{port}... attempt {attempt + 1}/{max_retries}")
            time.sleep(delay)
    return False


def wait_for_superset(base_url, max_retries=60, delay=10):
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/login/", timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"✓ Superset login page is ready after {attempt * delay} seconds")
                time.sleep(5)
                try:
                    csrf_response = requests.get(f"{base_url}/api/v1/security/csrf_token/", timeout=5)
                    if csrf_response.status_code in [200, 401, 403]:
                        print("✓ Superset API is responding")
                        return True
                except Exception:
                    pass
        except requests.exceptions.RequestException as e:
            print(f"⏳ Connection error: {str(e)}")
        print(f"⏳ Waiting for Superset... attempt {attempt + 1}/{max_retries}")
        time.sleep(delay)
    return False


def login_to_superset(base_url, username, password):
    session = requests.Session()
    login_response = session.post(
        f"{base_url}/api/v1/security/login",
        json={"username": username, "password": password, "provider": "db", "refresh": True},
    )
    login_response.raise_for_status()
    access_token = login_response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {access_token}"})
    csrf_response = session.get(f"{base_url}/api/v1/security/csrf_token/")
    csrf_response.raise_for_status()
    csrf_token = csrf_response.json()["result"]
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "X-CSRFToken": csrf_token,
        "Content-Type": "application/json",
    })
    print("✓ Successfully logged in to Superset")
    return session


def get_or_create_database(session, base_url):
    response = session.get(f"{base_url}/api/v1/database/")
    response.raise_for_status()
    for db in response.json()["result"]:
        if db["database_name"] == "Cube":
            print(f"✓ Database 'Cube' already exists (ID: {db['id']})")
            return db["id"]

    database_data = {
        "database_name": "Cube",
        "sqlalchemy_uri": "postgresql://root:{password}@{host}:{port}/db".format(
            password=os.environ.get("CUBEJS_SQL_PASSWORD", ""),
            host=os.environ.get("CUBE_HOST", "cube_api"),
            port=os.environ.get("CUBE_PORT", "15432"),
        ),
        "expose_in_sqllab": True,
        "allow_ctas": False,
        "allow_cvas": False,
        "allow_dml": True,
        "allow_file_upload": False,
    }
    print("🔄 Creating Cube database connection...")
    response = session.post(f"{base_url}/api/v1/database/", json=database_data)
    if response.status_code == 201:
        db_id = response.json()["id"]
        print(f"✓ Created Cube database connection (ID: {db_id})")
        return db_id
    else:
        print(f"✗ Failed to create database: {response.status_code} {response.text}")
        return None


def main():
    SUPERSET_URL = os.environ.get("SUPERSET_URL", "http://superset:8088")
    USERNAME = os.environ.get("SUPERSET_USERNAME", "admin")
    PASSWORD = os.environ.get("SUPERSET_PASSWORD", "admin")
    CUBE_HOST = os.environ.get("CUBE_HOST", "cube_api")
    CUBE_PORT = int(os.environ.get("CUBE_PORT", "15432"))

    print("🚀 Starting Superset connection setup...")

    if not wait_for_port(CUBE_HOST, CUBE_PORT):
        print("❌ Cube SQL failed to become ready")
        sys.exit(1)

    if not wait_for_superset(SUPERSET_URL):
        print("❌ Superset failed to become ready")
        sys.exit(1)

    try:
        session = login_to_superset(SUPERSET_URL, USERNAME, PASSWORD)
        db_id = get_or_create_database(session, SUPERSET_URL)
        if not db_id:
            sys.exit(1)
        print("🎉 Superset connection setup completed!")
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
