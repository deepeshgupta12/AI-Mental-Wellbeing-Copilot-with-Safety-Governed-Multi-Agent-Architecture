import { apiRequest } from "@/lib/api-client";
import type { CreateUserPayload, User } from "@/types/api";

export function createUser(payload: CreateUserPayload): Promise<User> {
  return apiRequest<User>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUser(userId: string): Promise<User> {
  return apiRequest<User>(`/api/v1/users/${userId}`);
}