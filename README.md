# repo-worker

Test repository for PrimeFlow repo-scoped workers (spec 021).

One repository, two teams, one directory each:

| Directory | Pool | Flows |
| --- | --- | --- |
| `flows/billing` | `billing` | `billing.invoice`, `shared.healthcheck` |
| `flows/network` | `network` | `network.sync`, `shared.healthcheck` |

Each directory runs its own code-pull worker (`python3 -m primeflow.code`) with
`PRIMEFLOW_CODE_SOURCE=repo-worker` and `PRIMEFLOW_CODE_PATH` set to its
directory. Each pool is bound to the same pair:

```bash
curl -X POST "$PRIMEFLOW_API_URL/api/v1/queues" -H "X-API-Key: $ADMIN_KEY" \
  -d '{"name":"billing","code_source":"repo-worker","code_path":"flows/billing"}'
```

`shared.healthcheck` is registered by both directories on purpose: the
catalogue keeps one owner per flow name and version, so the second worker's
publish of it is refused.
