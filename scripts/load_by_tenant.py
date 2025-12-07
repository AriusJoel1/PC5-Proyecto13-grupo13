"""
Uso:
  python scripts/load_by_tenant.py --tenant tenant-a --n 50 --delay 0.1
"""
import argparse
import time
import httpx


def run_load(url, tenant, n, delay):
    headers = {"X-Tenant-Id": tenant, "Content-Type": "application/json"}
    client = httpx.Client()
    for i in range(n):
        # alterna entre GET y PUT
        if i % 2 == 0:
            r = client.get(f"{url}/tenants/{tenant}/config", headers=headers, timeout=5.0)
            print(i, "GET", r.status_code)
        else:
            payload = {"config": {"iter": i, "msg": f"auto {i}"}}
            r = client.put(f"{url}/tenants/{tenant}/config", json=payload, headers=headers, timeout=5.0)
            print(i, "PUT", r.status_code)
        time.sleep(delay)
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", default="tenant-a")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    run_load(args.url, args.tenant, args.n, args.delay)
