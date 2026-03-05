import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api/client";

interface EnvVarsResponse {
  vars: Record<string, string>;
}

interface PromptResponse {
  content: string;
}

export function useEnvVars() {
  return useQuery<EnvVarsResponse>({
    queryKey: ["settings", "env"],
    queryFn: () => api.get("/settings/env").then((r) => r.data),
  });
}

export function useUpdateEnvVars() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: Record<string, string>) =>
      api.put("/settings/env", { vars }).then((r) => r.data as EnvVarsResponse),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings", "env"] }),
  });
}

export function usePrompt() {
  return useQuery<PromptResponse>({
    queryKey: ["settings", "prompt"],
    queryFn: () => api.get("/settings/prompt").then((r) => r.data),
  });
}

export function useUpdatePrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      api.put("/settings/prompt", { content }).then((r) => r.data as PromptResponse),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings", "prompt"] }),
  });
}
