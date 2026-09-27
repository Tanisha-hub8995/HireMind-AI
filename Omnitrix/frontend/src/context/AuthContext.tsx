import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  signup: (name: string, email: string, pass: string, role?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  demoLogin: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('hiremind_token') || localStorage.getItem('omnitrix_token'));
  const [loading, setLoading] = useState<boolean>(true);

  const fetchUser = async () => {
    try {
      const activeToken = localStorage.getItem('hiremind_token') || localStorage.getItem('omnitrix_token');
      if (activeToken) {
        const u = await api.getMe();
        setUser(u);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.warn('Could not restore user session:', err);
      localStorage.removeItem('hiremind_token');
      localStorage.removeItem('omnitrix_token');
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (email: string, pass: string) => {
    setLoading(true);
    try {
      const res = await api.login(email, pass);
      setToken(res.access_token);
      const u = await api.getMe();
      setUser(u);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (name: string, email: string, pass: string, role = 'user') => {
    setLoading(true);
    try {
      await api.signup({ name, email, password: pass, role });
      await login(email, pass);
    } finally {
      setLoading(false);
    }
  };

  const demoLogin = async () => {
    setLoading(true);
    const demoEmail = 'alex.chen@hiremind.ai';
    const demoPass = 'HireMindPass123!';
    try {
      try {
        await login(demoEmail, demoPass);
      } catch {
        // Fallback to legacy demo account if needed
        try {
          await login('alex.chen@omnitrix.ai', 'OmnitrixPass123!');
        } catch {
          // If neither exists, sign up demo user in DB
          await api.signup({
            name: 'Alex Chen',
            email: demoEmail,
            password: demoPass,
            role: 'user',
          });
          await login(demoEmail, demoPass);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('hiremind_token');
    localStorage.removeItem('omnitrix_token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        signup,
        logout,
        refreshUser,
        demoLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

const defaultAuth: AuthContextType = {
  user: null,
  token: null,
  loading: false,
  login: async () => {},
  signup: async () => {},
  logout: () => {},
  refreshUser: async () => {},
  demoLogin: async () => {},
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  return context || defaultAuth;
};
