import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

interface RequireAuthProps {
  children: React.ReactNode;
}

const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Wait for auth to finish loading before checking user
  if (loading) {
    return <LoadingSpinner message="Loading..." />;
  }

  if (!user) {
    return <Navigate to="/app/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default RequireAuth;


