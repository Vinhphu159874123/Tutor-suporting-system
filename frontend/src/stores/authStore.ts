import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authApi } from "../services/api";

declare const process: { env: Record<string, string | undefined> };
const isMockAdmin = process.env.REACT_APP_MOCK_ADMIN === "true";

export interface User {
  user_id: number;
  email: string;
  full_name: string;
  role: string[];  // Changed to array of roles
  available_roles?: string[]; // Same as role now (for backward compat)
  program?: string;
  faculty?: string;
  major?: string;
  phone?: string;
  bio?: string;
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
  currentMode: string | null; // Add current mode (can be different from user.role)
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  switchMode: (mode: string) => void; // Add method to switch mode
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      currentMode: null,

      login: async (email: string, password: string) => {
        if (isMockAdmin) {
          set({
            token: "mock-token",
            user: {
              user_id: 0,
              email,
              full_name: "Mock Admin",
              role: ["admin"],  // Array
              is_active: true,
              is_verified: true,
            } as User,
            isAuthenticated: true,
            isLoading: false,
            currentMode: "admin",
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
            currentMode: user.role[0], // Set initial mode to first role in array
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
          currentMode: null,
        });
      },

      setUser: (user: User) => {
        const { currentMode } = get();
        // Only set currentMode to user.role[0] if no currentMode is saved
        // This preserves the user's selected mode after refresh
        set({ 
          user, 
          currentMode: currentMode || user.role[0] 
        });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
      },

      switchMode: (mode: string) => {
        const { user } = get();
        // Check if mode exists in user's role array
        if (user?.role?.includes(mode)) {
          set({ currentMode: mode });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        currentMode: state.currentMode,
      }),
    }
  )
);

