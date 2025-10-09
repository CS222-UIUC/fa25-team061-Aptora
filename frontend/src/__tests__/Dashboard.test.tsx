import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../utils/testUtils';
import Dashboard from '../pages/Dashboard';
import { mockDashboardStats, mockUpcomingAssignments } from '../utils/mockData';

// Mock react-query
jest.mock('react-query', () => ({
  useQuery: jest.fn(),
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    const { useQuery } = require('react-query');
    
    useQuery
      .mockReturnValueOnce({
        data: mockDashboardStats,
        isLoading: false,
      })
      .mockReturnValueOnce({
        data: mockUpcomingAssignments,
        isLoading: false,
      });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard with statistics cards', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Total Courses')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // total_courses
    expect(screen.getByText('Total Assignments')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // total_assignments
    expect(screen.getByText('Upcoming')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // upcoming_assignments
    expect(screen.getByText('Completed Sessions')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument(); // completed_sessions
  });

  it('renders upcoming assignments section', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Upcoming Assignments')).toBeInTheDocument();
    expect(screen.getByText('Binary Search Tree Implementation')).toBeInTheDocument();
    expect(screen.getByText('Midterm Exam')).toBeInTheDocument();
    expect(screen.getByText('Data Structures and Algorithms')).toBeInTheDocument();
  });

  it('renders quick actions section', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Add Course')).toBeInTheDocument();
    expect(screen.getByText('Add Assignment')).toBeInTheDocument();
    expect(screen.getByText('Generate Schedule')).toBeInTheDocument();
    expect(screen.getByText('Set Availability')).toBeInTheDocument();
  });

  it('shows difficulty chips for assignments', () => {
    render(<Dashboard />);
    
    const hardChips = screen.getAllByText('hard');
    expect(hardChips).toHaveLength(2); // Both assignments are hard difficulty
  });

  it('shows loading state when data is being fetched', () => {
    const { useQuery } = require('react-query');
    
    useQuery
      .mockReturnValueOnce({
        data: undefined,
        isLoading: true,
      })
      .mockReturnValueOnce({
        data: undefined,
        isLoading: true,
      });
    
    render(<Dashboard />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no upcoming assignments', () => {
    const { useQuery } = require('react-query');
    
    useQuery
      .mockReturnValueOnce({
        data: mockDashboardStats,
        isLoading: false,
      })
      .mockReturnValueOnce({
        data: [],
        isLoading: false,
      });
    
    render(<Dashboard />);
    
    expect(screen.getByText('No upcoming assignments')).toBeInTheDocument();
  });

  it('navigates to assignments page when View All button is clicked', async () => {
    const user = userEvent.setup();
    const mockNavigate = jest.fn();
    
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
    
    render(<Dashboard />);
    
    const viewAllButton = screen.getByText('View All');
    await user.click(viewAllButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/assignments');
  });

  it('navigates to courses page when Add Course button is clicked', async () => {
    const user = userEvent.setup();
    const mockNavigate = jest.fn();
    
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
    
    render(<Dashboard />);
    
    const addCourseButton = screen.getByText('Add Course');
    await user.click(addCourseButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/courses');
  });
});
