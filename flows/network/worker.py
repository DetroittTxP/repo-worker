"""Network team's PrimeFlow worker.

Run under the code-pull supervisor so the flow version is the commit SHA:

    PRIMEFLOW_CODE_REPO=https://github.com/DetroittTxP/repo-worker.git \\
    PRIMEFLOW_CODE_PATH=flows/network \\
    PRIMEFLOW_CODE_SOURCE=repo-worker \\
    PRIMEFLOW_QUEUES=network \\
    python3 -m primeflow.code
"""

import primeflow


def sync(ctx: primeflow.Context):
    site = (ctx.params or {}).get("site", "lab")
    return ctx.task("sync", lambda c: {"team": "network", "site": site, "synced": True, "rev": 3})


def healthcheck(ctx: primeflow.Context):
    return ctx.task("ping", lambda c: {"team": "network", "ok": True})


def register() -> primeflow.Registry:
    r = primeflow.Registry()
    r.register("network.sync", sync, description="Sync one site.", tags=("repo-worker",))
    # Same name as the billing directory's flow, on purpose.
    r.register("shared.healthcheck", healthcheck, description="Network health check.", tags=("repo-worker",))
    return r


if __name__ == "__main__":
    primeflow.Worker(register(), concurrency=4).run()
