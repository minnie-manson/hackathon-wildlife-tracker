import os

from supabase import create_client, Client
from dotenv import load_dotenv

url: str = "https://nnwmzsxixhrvfkcszgzi.supabase.co"
load_dotenv()
key: str = os.getenv("SUPABASE_API_KEY")

supabase: Client = create_client(supabase_url=url, supabase_key=key)


# PyPi Docs - for API calls
# https://supabase.com/docs/reference/python/introduction
