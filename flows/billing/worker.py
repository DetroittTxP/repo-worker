"""Billing team's PrimeFlow worker.

Run under the code-pull supervisor so the flow version is the commit SHA:

    PRIMEFLOW_CODE_REPO=https://github.com/DetroittTxP/repo-worker.git \\
    PRIMEFLOW_CODE_PATH=flows/billing \\
    PRIMEFLOW_CODE_SOURCE=repo-worker \\
    PRIMEFLOW_QUEUES=billing \\
    python3 -m primeflow.code
"""

import primeflow


def invoice(ctx: primeflow.Context):
    ticket = (ctx.params or {}).get("ticket", "T-0")
    return ctx.task("issue", lambda c: {"team": "billing", "ticket": ticket, "issued": True})


def healthcheck(ctx: primeflow.Context):
    return ctx.task("ping", lambda c: {"team": "billing", "ok": True})


def approve(ctx: primeflow.Context):
    """Wait for a person to approve the invoice, then record the answer.

    The run pauses on the wait. A push to another directory of the repo must
    not move this worker's version, so the run resumes on the same commit."""
    ticket = (ctx.params or {}).get("ticket", "T-0")
    answer = ctx.await_signal("approve", prompt="Approve this invoice?", no_deadline=True)
    return ctx.task("record", lambda c: {"team": "billing", "ticket": ticket, "answer": answer})


def register() -> primeflow.Registry:
    r = primeflow.Registry()
    r.register("billing.invoice", invoice, description="Issue one invoice.", tags=("repo-worker",))
    r.register("billing.approve", approve, description="Wait for approval, then record it.", tags=("repo-worker",))
    # Both directories register a flow with this name on purpose: the
    # catalogue keeps one owner per name and version.
    r.register("shared.healthcheck", healthcheck, description="Billing health check.", tags=("repo-worker",))
    return r


if __name__ == "__main__":
    primeflow.Worker(register(), concurrency=4).run()
