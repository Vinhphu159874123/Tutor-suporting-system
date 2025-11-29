import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authApi } from "../services/api";

declare const process: { env: Record<string, string | undefined> };
const isMockAdmin = process.env.REACT_APP_MOCK_ADMIN === "true";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  faculty?: string;
  major?: string;
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        if (isMockAdmin) {
          set({
            token: "mock-token",
            user: {
              id: 0,
              email,
              full_name: "Mock Admin",
              role: "admin",
              is_active: true,
              is_verified: true,
            } as User,
            isAuthenticated: true,
            isLoading: false,
          });
          return;
        }
        set({ isLoading: true });
        try {
          const response: any = await authApi.login(email, password);
          const { access_token } = response.data;

          // Get user profile
          const userResponse: any = await authApi.getProfile(access_token);
          const user = userResponse.data;

          set({
            token: access_token,
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

