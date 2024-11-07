import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth, UserRole } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
  redirectTo = '/login'
}) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        // Not authenticated
        router.push(redirectTo);
      } else if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        // Not authorized for this role
        switch (user.role) {
          case 'student':
            router.push('/student/dashboard');
            break;
          case 'teacher':
            router.push('/teacher/dashboard');
            break;
          case 'guardian':
            router.push('/guardian/dashboard');
            break;
          case 'admin':
            router.push('/admin/dashboard');
            break;
          default:
            router.push('/');
        }
      }
    }
  }, [user, loading, allowedRoles, redirectTo, router]);

  // Show nothing while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Not authenticated or not authorized
  if (!user || (allowedRoles.length > 0 && !allowedRoles.includes(user.role))) {
    return null;
  }

  // Authenticated and authorized
  return <>{children}</>;
};

// Higher-order components for specific roles
export const StudentRoute: React.FC<Omit<ProtectedRouteProps, 'allowedRoles'>> = (props) => (
  <ProtectedRoute {...props} allowedRoles={['student', 'admin']} />
);

export const TeacherRoute: React.FC<Omit<ProtectedRouteProps, 'allowedRoles'>> = (props) => (
  <ProtectedRoute {...props} allowedRoles={['teacher', 'admin']} />
);

export const GuardianRoute: React.FC<Omit<ProtectedRouteProps, 'allowedRoles'>> = (props) => (
  <ProtectedRoute {...props} allowedRoles={['guardian', 'admin']} />
);

export const AdminRoute: React.FC<Omit<ProtectedRouteProps, 'allowedRoles'>> = (props) => (
  <ProtectedRoute {...props} allowedRoles={['admin']} />
);

// Custom hook for checking route access
export const useRouteAccess = (allowedRoles: UserRole[] = []) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    } else if (
      !loading &&
      user &&
      allowedRoles.length > 0 &&
      !allowedRoles.includes(user.role)
    ) {
      switch (user.role) {
        case 'student':
          router.push('/student/dashboard');
          break;
        case 'teacher':
          router.push('/teacher/dashboard');
          break;
        case 'guardian':
          router.push('/guardian/dashboard');
          break;
        case 'admin':
          router.push('/admin/dashboard');
          break;
        default:
          router.push('/');
      }
    }
  }, [user, loading, allowedRoles, router]);

  return { isAllowed: user && allowedRoles.includes(user.role), loading };
};

export default ProtectedRoute;
