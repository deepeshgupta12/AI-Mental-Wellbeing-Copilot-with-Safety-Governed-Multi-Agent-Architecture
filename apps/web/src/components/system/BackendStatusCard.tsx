import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getHealth, getHealthDependencies } from "@/lib/health-api";

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block h-2.5 w-2.5 rounded-full ${
        ok ? "bg-green-500" : "bg-red-500"
      }`}
      aria-hidden="true"
    />
  );
}

export function BackendStatusCard() {
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
  });

  const dependenciesQuery = useQuery({
    queryKey: ["health", "dependencies"],
    queryFn: getHealthDependencies,
  });

  const loading = healthQuery.isLoading || dependenciesQuery.isLoading;
  const error = healthQuery.isError || dependenciesQuery.isError;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">System status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <p className="text-sm text-muted-foreground">
            Checking backend connectivity...
          </p>
        ) : error ? (
          <p className="text-sm text-red-600">
            Unable to connect to backend services.
          </p>
        ) : (
          <>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">API</p>
                <p className="text-xs text-muted-foreground">
                  {healthQuery.data?.service} · {healthQuery.data?.environment}
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm font-medium">
                <StatusDot ok={healthQuery.data?.status === "ok"} />
                <span>{healthQuery.data?.status}</span>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Postgres</p>
                <p className="text-xs text-muted-foreground">
                  Database connectivity
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm font-medium">
                <StatusDot
                  ok={dependenciesQuery.data?.dependencies.postgres.status === "ok"}
                />
                <span>{dependenciesQuery.data?.dependencies.postgres.status}</span>
              </div>
            </div>

            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Redis</p>
                <p className="text-xs text-muted-foreground">
                  Cache and async runtime
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm font-medium">
                <StatusDot
                  ok={dependenciesQuery.data?.dependencies.redis.status === "ok"}
                />
                <span>{dependenciesQuery.data?.dependencies.redis.status}</span>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}