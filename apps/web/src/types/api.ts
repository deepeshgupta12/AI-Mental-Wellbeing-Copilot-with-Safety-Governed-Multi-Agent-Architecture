export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  environment: string;
};

export type DependencyStatus = "ok" | "error";

export type HealthDependenciesResponse = {
  status: "ok" | "degraded";
  dependencies: {
    postgres: {
      status: DependencyStatus;
      error: string | null;
    };
    redis: {
      status: DependencyStatus;
      error: string | null;
    };
  };
};