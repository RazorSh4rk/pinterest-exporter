import os
from dotenv import load_dotenv
from b2sdk.v2 import InMemoryAccountInfo, B2Api, AuthInfoCache

load_dotenv()

bucketname = "pinterest-pdf-exports"

b2 = None

def setup():
    global b2
    info = InMemoryAccountInfo()
    b2 = B2Api(info, cache=AuthInfoCache(info))
    application_key_id = os.environ["B2_KEY_ID"]
    application_key = os.environ["B2_APPLICATION_KEY"]
    b2.authorize_account("production", application_key_id, application_key)

def upload_file(local_fpath, remote_fname):
    bucket = b2.get_bucket_by_name(bucketname)
    bucket.upload_local_file(
        local_file=local_fpath,
        file_name=remote_fname
    )

def get_download_url(remote_fname):
    bucket = b2.get_bucket_by_name(bucketname)
    return bucket.get_download_url(remote_fname)

