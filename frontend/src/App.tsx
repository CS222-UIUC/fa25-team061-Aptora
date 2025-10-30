import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';
import LandingPage from './pages/LandingPage';
import AppRouter from './components/AppRouter';
import RequireAuth from './components/RequireAuth';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider } from './contexts/AuthContext';
import About from './pages/About';

const theme = createTheme({
  palette: {
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#ec4899',
      light: '#f472b6',
      dark: '#db2777',
    },
    background: {
      default: '#fafafa',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '3.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 600,
      fontSize: '2.5rem',
      lineHeight: 1.3,
    },
    h3: {
      fontWeight: 600,
      fontSize: '2rem',
      lineHeight: 1.4,
    },
  },
  shape: {
    borderRadius: 12,
  },
});

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              {/* Public auth routes */}
              <Route path="/app/login" element={<Login />} />
              <Route path="/app/register" element={<Register />} />
              <Route path="/login" element={<Navigate to="/app/login" replace />} />
              <Route path="/register" element={<Navigate to="/app/register" replace />} />
              {/* Public About */}
              <Route path="/app/about" element={<About />} />
              <Route path="/about" element={<Navigate to="/app/about" replace />} />

              {/* Protected app routes */}
              <Route
                path="/app/*"
                element={
                  <RequireAuth>
                    <AppRouter />
                  </RequireAuth>
                }
              />
              <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
              <Route path="/courses" element={<Navigate to="/app/courses" replace />} />
              <Route path="/assignments" element={<Navigate to="/app/assignments" replace />} />
              <Route path="/schedule" element={<Navigate to="/app/schedule" replace />} />
              <Route path="/calendar" element={<Navigate to="/app/calendar" replace />} />
              <Route path="/availability" element={<Navigate to="/app/availability" replace />} />
              <Route path="/admin" element={<Navigate to="/app/admin" replace />} />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;