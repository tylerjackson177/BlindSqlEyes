# BlindSqlEyes

This Python script automates a **blind SQL injection** attack against a CTF login endpoint.  
Given a vulnerable `users(user__name, passwd)` table, it:

1. Counts rows in `users`.  
2. Extracts each `user__name` one character at a time.  
3. For each username, extracts its `passwd`.  

One of the passwords will be your `{…}` flag.

---

## 🛠️ Prerequisites

- Python 3.6+  
- `requests` library  
  ```bash
  pip install requests
