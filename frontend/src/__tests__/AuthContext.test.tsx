import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { mockUser } from '../utils/mockData';

// Mock axios
jest.mock('axios');
const mockAxios = require('axios');

// Test component that uses the auth context
const TestComponent: React.FC = () => {
  const { user, login, register, logout } = useAuth();
  
  return (
    <div>
      <div data-testid="user-email">{user?.email || 'No user'}</div>
      <button onClick={() => login('test@example.com', 'password')}>
        Login
      </button>
      <button onClick={() => register('test@example.com', 'password', 'John', 'Doe')}>
        Register
      </button>
      <button onClick={logout}>
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage
    localStorage.clear();
    // Reset axios defaults
    delete mockAxios.defaults.headers.common['Authorization'];
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('provides initial state with no user', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
  });

  it('loads user from localStorage on mount', async () => {
    localStorage.setItem('access_token', 'fake-token');
    mockAxios.defaults.headers.common['Authorization'] = 'Bearer fake-token';
    mockAxios.get.mockResolvedValueOnce({ data: mockUser });
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent(mockUser.email);
    });
  });

  it('handles login successfully', async () => {
    const user = userEvent.setup();
    mockAxios.post.mockResolvedValueOnce({
      data: { access_token: 'fake-token' }
    });
    mockAxios.get.mockResolvedValueOnce({ data: mockUser });
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    const loginButton = screen.getByText('Login');
    await user.click(loginButton);
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('fake-token');
      expect(mockAxios.defaults.headers.common['Authorization']).toBe('Bearer fake-token');
      expect(screen.getByTestId('user-email')).toHaveTextContent(mockUser.email);
    });
  });

  it('handles login failure', async () => {
    const user = userEvent.setup();
    mockAxios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Invalid credentials' } }
    });
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    const loginButton = screen.getByText('Login');
    await user.click(loginButton);
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
    });
  });

  it('handles registration successfully', async () => {
    const user = userEvent.setup();
    mockAxios.post.mockResolvedValueOnce({ data: {} });
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    const registerButton = screen.getByText('Register');
    await user.click(registerButton);
    
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledWith('/auth/register', {
        email: 'test@example.com',
        password: 'password',
        first_name: 'John',
        last_name: 'Doe',
      });
    });
  });

  it('handles registration failure', async () => {
    const user = userEvent.setup();
    mockAxios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Email already exists' } }
    });
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    const registerButton = screen.getByText('Register');
    await user.click(registerButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
    });
  });

  it('handles logout', async () => {
    const user = userEvent.setup();
    localStorage.setItem('access_token', 'fake-token');
    mockAxios.defaults.headers.common['Authorization'] = 'Bearer fake-token';
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    const logoutButton = screen.getByText('Logout');
    await user.click(logoutButton);
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(mockAxios.defaults.headers.common['Authorization']).toBeUndefined();
      expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
    });
  });

  it('handles fetch user error', async () => {
    localStorage.setItem('access_token', 'invalid-token');
    mockAxios.defaults.headers.common['Authorization'] = 'Bearer invalid-token';
    mockAxios.get.mockRejectedValueOnce(new Error('Unauthorized'));
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(mockAxios.defaults.headers.common['Authorization']).toBeUndefined();
      expect(screen.getByTestId('user-email')).toHaveTextContent('No user');
    });
  });
});
