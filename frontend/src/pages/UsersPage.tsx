import { useState, type FormEvent } from "react";
import {
  useUsersList,
  useCreateUser,
  useUpdateUser,
  useDeleteUser,
  type UserSummary,
} from "../hooks/useUsers";
import { useAuth } from "../hooks/useAuth";
import { toast } from "../components/Toast";

const ROLE_LABELS: Record<string, string> = {
  admin: "Administrador",
  manager: "Gerente",
  consulta: "Consulta",
};

const ROLE_STYLES: Record<string, string> = {
  admin: "bg-red-100 text-red-700",
  manager: "bg-blue-100 text-blue-700",
  consulta: "bg-gray-100 text-gray-600",
};

export default function UsersPage() {
  const { user: me } = useAuth();
  const isAdmin = me?.role === "admin";
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const { data, isLoading, isError } = useUsersList({
    search: search || undefined,
    role: roleFilter || undefined,
  });
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<UserSummary | null>(null);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Usuarios</h2>
        {isAdmin && (
          <button
            onClick={() => {
              setEditing(null);
              setShowForm(true);
            }}
            className="bg-navy-700 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-navy-600 transition"
          >
            Novo Usuario
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Buscar por nome ou email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 focus:border-navy-500 outline-none"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
        >
          <option value="">Todos os perfis</option>
          <option value="admin">Administrador</option>
          <option value="manager">Gerente</option>
          <option value="consulta">Consulta</option>
        </select>
      </div>

      {/* Modal */}
      {showForm && (
        <UserFormModal
          user={editing}
          onClose={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      )}

      {/* Table */}
      {isError ? (
        <p className="text-red-600">Erro ao carregar usuarios.</p>
      ) : isLoading ? (
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-14 bg-gray-100 rounded-lg" />
          ))}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-5 py-3 font-medium">Nome</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium">Perfil</th>
                <th className="px-5 py-3 font-medium">Criado em</th>
                {isAdmin && (
                  <th className="px-5 py-3 font-medium text-right">Acoes</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-900">
                    {u.nome}
                  </td>
                  <td className="px-5 py-3 text-gray-600">{u.email}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`text-xs px-2 py-1 rounded font-medium ${
                        ROLE_STYLES[u.role] || "bg-gray-100"
                      }`}
                    >
                      {ROLE_LABELS[u.role] || u.role}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-500">
                    {new Date(u.created_at).toLocaleDateString("pt-BR")}
                  </td>
                  {isAdmin && (
                    <td className="px-5 py-3 text-right space-x-2">
                      <button
                        onClick={() => {
                          setEditing(u);
                          setShowForm(true);
                        }}
                        className="text-navy-600 hover:text-navy-800 font-medium"
                      >
                        Editar
                      </button>
                      {u.id !== me?.id && <DeleteButton userId={u.id} />}
                    </td>
                  )}
                </tr>
              ))}
              {data?.users.length === 0 && (
                <tr>
                  <td
                    colSpan={isAdmin ? 5 : 4}
                    className="px-5 py-8 text-center text-gray-500"
                  >
                    Nenhum usuario encontrado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function DeleteButton({ userId }: { userId: string }) {
  const deleteUser = useDeleteUser();
  const [confirming, setConfirming] = useState(false);

  if (confirming) {
    return (
      <span className="inline-flex gap-1">
        <button
          onClick={() => {
            deleteUser.mutate(userId, {
              onSuccess: () => {
                toast("Usuario excluido.", "success");
                setConfirming(false);
              },
              onError: () => toast("Erro ao excluir usuario."),
            });
          }}
          disabled={deleteUser.isPending}
          className="text-red-600 hover:text-red-800 font-medium"
        >
          Confirmar
        </button>
        <button
          onClick={() => setConfirming(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          Cancelar
        </button>
      </span>
    );
  }

  return (
    <button
      onClick={() => setConfirming(true)}
      className="text-red-500 hover:text-red-700 font-medium"
    >
      Excluir
    </button>
  );
}

function UserFormModal({
  user,
  onClose,
}: {
  user: UserSummary | null;
  onClose: () => void;
}) {
  const isEdit = !!user;
  const createUser = useCreateUser();
  const updateUser = useUpdateUser();
  const [nome, setNome] = useState(user?.nome || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(user?.role || "consulta");
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    try {
      if (isEdit) {
        const data: Record<string, string> = {};
        if (nome !== user.nome) data.nome = nome;
        if (email !== user.email) data.email = email;
        if (role !== user.role) data.role = role;
        if (password) data.password = password;
        await updateUser.mutateAsync({ id: user.id, data });
        toast("Usuario atualizado.", "success");
      } else {
        if (!password) {
          setError("Senha e obrigatoria para novo usuario.");
          return;
        }
        await createUser.mutateAsync({ nome, email, password, role });
        toast("Usuario criado.", "success");
      }
      onClose();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Erro ao salvar usuario.";
      setError(msg);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          {isEdit ? "Editar Usuario" : "Novo Usuario"}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome
            </label>
            <input
              type="text"
              required
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Senha{isEdit && " (deixe vazio para manter)"}
            </label>
            <input
              type="password"
              required={!isEdit}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
              placeholder={isEdit ? "••••••••" : ""}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Perfil
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-navy-500 outline-none"
            >
              <option value="admin">Administrador</option>
              <option value="manager">Gerente</option>
              <option value="consulta">Consulta</option>
            </select>
          </div>

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={createUser.isPending || updateUser.isPending}
              className="flex-1 bg-navy-700 text-white py-2.5 rounded-lg font-medium hover:bg-navy-600 disabled:opacity-50 transition"
            >
              {isEdit ? "Salvar" : "Criar"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 py-2.5 rounded-lg font-medium hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
