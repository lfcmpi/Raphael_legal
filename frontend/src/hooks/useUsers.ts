import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api/client";

export interface UserSummary {
  id: string;
  email: string;
  nome: string;
  role: string;
  created_at: string;
}

interface UserListResponse {
  users: UserSummary[];
  total: number;
}

interface UserFilters {
  search?: string;
  role?: string;
  page?: number;
}

interface CreateUserData {
  email: string;
  nome: string;
  password: string;
  role: string;
}

interface UpdateUserData {
  email?: string;
  nome?: string;
  password?: string;
  role?: string;
}

export function useUsersList(filters: UserFilters = {}) {
  const params = new URLSearchParams();
  if (filters.search) params.set("search", filters.search);
  if (filters.role) params.set("role", filters.role);
  if (filters.page) params.set("page", String(filters.page));

  return useQuery<UserListResponse>({
    queryKey: ["users", filters],
    queryFn: () => api.get(`/users?${params}`).then((r) => r.data),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateUserData) =>
      api.post("/users", data).then((r) => r.data as UserSummary),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserData }) =>
      api.patch(`/users/${id}`, data).then((r) => r.data as UserSummary),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/users/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}
