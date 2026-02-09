import os
import b2

def test_setup():
    """Test B2 authentication"""
    b2.setup()
    assert b2.b2 is not None
    print("setup: OK")

def test_upload_file():
    """Test uploading a file to B2"""
    b2.setup()
    local_file = "requirements.txt"
    remote_name = "test/requirements.txt"
    b2.upload_file(local_file, remote_name)
    print(f"upload_file: OK - uploaded {local_file} as {remote_name}")

def test_get_download_url():
    """Test getting download URL"""
    b2.setup()
    remote_name = "test/requirements.txt"
    url = b2.get_download_url(remote_name)
    assert url is not None
    assert "backblaze" in url or "b2" in url
    print(f"get_download_url: OK - {url}")

if __name__ == "__main__":
    test_setup()
    test_upload_file()
    test_get_download_url()
    print("\nAll tests passed!")
