import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

export default function ProtectedRoute({ 
  children, 
  requiredRoles = [] 
}: ProtectedRouteProps) {
  const { user, loading, error } = useAuth();
  const router = useRouter();
  const [hasRequiredRole, setHasRequiredRole] = useState(false);
  const [checkingRole, setCheckingRole] = useState(false);

  useEffect(() => {
    async function checkUserRole() {
      if (user && requiredRoles.length > 0) {
        setCheckingRole(true);
        try {
          const tokenResult = await user.getIdTokenResult();
          const userRole = tokenResult.claims.role as string;
          setHasRequiredRole(userRole ? requiredRoles.includes(userRole) : false);
        } catch (error) {
          console.error('Error checking user role:', error);
          setHasRequiredRole(false);
        }
        setCheckingRole(false);
      }
    }

    if (!loading) {
      if (!user) {
        router.push('/login');
      } else if (requiredRoles.length > 0) {
        checkUserRole();
      }
    }
  }, [user, loading, router, requiredRoles]);

  // Show loading spinner while checking authentication or role
  if (loading || checkingRole) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
      </div>
    );
  }

  // Show error message if authentication fails
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  // If roles are required, check if user has required role
  if (requiredRoles.length > 0 && !hasRequiredRole) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Unauthorized: </strong>
          <span className="block sm:inline">You don&apos;t have permission to access this page.</span>
        </div>
      </div>
    );
  }

  // If user is authenticated and has required role (if any), render children
  if (user && (!requiredRoles.length || hasRequiredRole)) {
    return <>{children}</>;
  }

  // Return null while redirecting
  return null;
}
