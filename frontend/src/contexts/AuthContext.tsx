import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  User as FirebaseUser,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  getAuth,
} from 'firebase/auth';
import { app } from '../config/firebase';

export type UserRole = 'student' | 'teacher' | 'guardian' | 'admin';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  firebase_uid: string;
  is_active: boolean;
  profile_picture?: string;
  grade_level?: string;
  subjects?: string;
}

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const auth = getAuth(app);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setFirebaseUser(firebaseUser);
      setLoading(true);

      try {
        if (firebaseUser) {
          // Get ID token for backend authentication
          const idToken = await firebaseUser.getIdToken();

          // Fetch user data from backend
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${idToken}`
            }
          });

          if (!response.ok) {
            throw new Error('Failed to fetch user data');
          }

          const userData: User = await response.json();
          setUser(userData);
        } else {
          setUser(null);
        }
      } catch (err) {
        console.error('Auth state change error:', err);
        setError(err instanceof Error ? err.message : 'Authentication error');
        setUser(null);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [auth]);

  const signIn = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();

      // Login with backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const userData: User = await response.json();
      setUser(userData);
    } catch (err) {
      console.error('Sign in error:', err);
      setError(err instanceof Error ? err.message : 'Sign in failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setLoading(true);
      await firebaseSignOut(auth);
      setUser(null);
    } catch (err) {
      console.error('Sign out error:', err);
      setError(err instanceof Error ? err.message : 'Sign out failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  const value = {
    user,
    firebaseUser,
    loading,
    error,
    signIn,
    signOut,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hooks for role-based access
export const useIsStudent = () => {
  const { user } = useAuth();
  return user?.role === 'student';
};

export const useIsTeacher = () => {
  const { user } = useAuth();
  return user?.role === 'teacher';
};

export const useIsGuardian = () => {
  const { user } = useAuth();
  return user?.role === 'guardian';
};

export const useIsAdmin = () => {
  const { user } = useAuth();
  return user?.role === 'admin';
};

export const useAuthorized = (allowedRoles: UserRole[]) => {
  const { user } = useAuth();
  return user ? allowedRoles.includes(user.role) : false;
};
