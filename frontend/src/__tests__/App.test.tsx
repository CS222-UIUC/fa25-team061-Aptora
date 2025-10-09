import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../utils/testUtils';
import App from '../App';

// Mock the auth context
jest.mock('../contexts/AuthContext');
const mockUseAuth = require('../contexts/AuthContext').useAuth;

describe('App Component', () => {
  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders login page when user is not authenticated', () => {
    render(<App />);
    
    expect(screen.getByText('Smart Study Scheduler')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('renders dashboard when user is authenticated', () => {
    const mockUser = {
      id: 1,
      email: 'test@example.com',
      first_name: 'John',
      last_name: 'Doe',
      is_active: true,
    };
    
    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
    
    render(<App />);
    
    expect(screen.getByText('Smart Study Scheduler')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('shows loading state when authentication is being checked', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: true,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
    
    render(<App />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('navigates to different pages when navigation items are clicked', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: 1,
      email: 'test@example.com',
      first_name: 'John',
      last_name: 'Doe',
      is_active: true,
    };
    
    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
    
    render(<App />);
    
    // Click on Courses navigation
    const coursesButton = screen.getByText('Courses');
    await user.click(coursesButton);
    
    await waitFor(() => {
      expect(screen.getByText('Courses')).toBeInTheDocument();
    });
    
    // Click on Assignments navigation
    const assignmentsButton = screen.getByText('Assignments');
    await user.click(assignmentsButton);
    
    await waitFor(() => {
      expect(screen.getByText('Assignments')).toBeInTheDocument();
    });
  });

  it('redirects authenticated user from login page to dashboard', () => {
    const mockUser = {
      id: 1,
      email: 'test@example.com',
      first_name: 'John',
      last_name: 'Doe',
      is_active: true,
    };
    
    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
    
    // Navigate to login page
    window.history.pushState({}, 'Login', '/login');
    render(<App />);
    
    // Should redirect to dashboard
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('redirects unauthenticated user from protected routes to login', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
    });
    
    // Navigate to protected route
    window.history.pushState({}, 'Dashboard', '/dashboard');
    render(<App />);
    
    // Should redirect to login
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('handles logout functionality', async () => {
    const user = userEvent.setup();
    const mockLogout = jest.fn();
    const mockUser = {
      id: 1,
      email: 'test@example.com',
      first_name: 'John',
      last_name: 'Doe',
      is_active: true,
    };
    
    mockUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      login: jest.fn(),
      register: jest.fn(),
      logout: mockLogout,
    });
    
    render(<App />);
    
    // Click on user menu
    const accountButton = screen.getByTestId('AccountCircleIcon');
    await user.click(accountButton);
    
    // Click logout
    const logoutButton = screen.getByText('Logout');
    await user.click(logoutButton);
    
    expect(mockLogout).toHaveBeenCalled();
  });
});
