from supabase_client import supabase
from datetime import datetime


# ---- AUTH ----


def register_user(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

def login_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

# ---- PLACES ----


def list_places(limit: int = 25):
    return supabase.table("places").select("*", count="exact").order("created_at", desc=True).limit(limit).execute()




def create_place(user_id: str, name: str, description: str, lat: float, lng: float, photo_url: str | None = None):
    data = {
        "user_id": user_id,
        "name": name,
        "description": description,
        "lat": lat,
        "lng": lng,
        "photo_url": photo_url,
        "created_at": datetime.utcnow().isoformat()
    }
    return supabase.table("places").insert(data).execute()




def get_place(place_id: str):
    return supabase.table("places").select("*", count="exact").eq("id", place_id).single().execute()




def rate_place(place_id: str, user_id: str, rating: int, comment: str | None = None):
    payload = {
        "place_id": place_id,
        "user_id": user_id,
        "rating": rating,
        "comment": comment
    }
    return supabase.table("ratings").insert(payload).execute()




# ---- STORAGE (opcional) ----

def upload_place_photo(file_bytes: bytes, filename: str) -> str:
    """Sube a bucket 'places' y devuelve la URL pública"""
    bucket = supabase.storage.from_("places")
    bucket.upload(path=filename, file=file_bytes, file_options={"cache-control":
    "3600", "upsert": True})
    public_url = bucket.get_public_url(filename)
    return public_url