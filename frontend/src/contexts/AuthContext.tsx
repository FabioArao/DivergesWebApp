import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { 
  User,
  onAuthStateChanged,
  signOut as firebaseSignOut,
  onIdTokenChanged
} from "firebase/auth";
import { auth } from "../config/firebase";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  token: string | null;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  error: null,
  token: null,
  signOut: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Handle token refresh
  useEffect(() => {
    const unsubscribe = onIdTokenChanged(auth, async (user) => {
      if (user) {
        try {
          const token = await user.getIdToken();
          setToken(token);
          // Store token in secure httpOnly cookie via API call
          await fetch('/api/auth/session', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token }),
          });
        } catch (error) {
          console.error('Error refreshing token:', error);
          setError('Failed to refresh authentication token');
        }
      } else {
        setToken(null);
        // Clear token cookie via API call
        await fetch('/api/auth/session', { method: 'DELETE' });
      }
    });

    return () => unsubscribe();
  }, []);

  // Handle auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      try {
        if (user) {
          // Get fresh token
          const token = await user.getIdToken(true);
          setToken(token);
          setUser(user);
        } else {
          setUser(null);
          setToken(null);
        }
      } catch (error) {
        console.error('Auth state change error:', error);
        setError('Authentication error occurred');
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  // Sign out function
  const signOut = useCallback(async () => {
    try {
      await firebaseSignOut(auth);
      setUser(null);
      setToken(null);
      // Clear session cookie
      await fetch('/api/auth/session', { method: 'DELETE' });
    } catch (error) {
      console.error('Sign out error:', error);
      setError('Failed to sign out');
    }
  }, []);

  // Reset error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <AuthContext.Provider value={{ user, loading, error, token, signOut }}>
      {!loading ? (
        children
      ) : (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
        </div>
      )}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
