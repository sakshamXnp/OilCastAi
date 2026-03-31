import urllib.request

url = "https://oilcast-ai-backend-production.up.railway.app/api/commodities"
req = urllib.request.Request(url, method="OPTIONS")
req.add_header("Origin", "https://oil-cast-ai.vercel.app")
req.add_header("Access-Control-Request-Method", "GET")

with open("cors_result.txt", "w", encoding="utf-8") as f:
    try:
        with urllib.request.urlopen(req) as response:
            f.write(f"Status: {response.status}\n")
            f.write("Headers:\n")
            for k, v in response.headers.items():
                f.write(f"{k}: {v}\n")
    except urllib.error.URLError as e:
        f.write(f"Error: {e}\n")
        if hasattr(e, 'headers'):
            f.write("Headers:\n")
            for k, v in e.headers.items():
                f.write(f"{k}: {v}\n")
