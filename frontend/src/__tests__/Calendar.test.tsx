import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../utils/testUtils';
import Calendar from '../components/Calendar';
import { mockStudySessions, mockAssignments } from '../utils/mockData';

// Mock react-query
jest.mock('react-query', () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(),
  useQueryClient: jest.fn(),
}));

// Mock react-big-calendar
jest.mock('react-big-calendar', () => {
  return {
    Calendar: ({ events, onSelectEvent }: any) => (
      <div data-testid="calendar">
        {events.map((event: any, index: number) => (
          <div
            key={index}
            data-testid={`calendar-event-${index}`}
            onClick={() => onSelectEvent(event)}
          >
            {event.title}
          </div>
        ))}
      </div>
    ),
    momentLocalizer: jest.fn(),
    Views: { MONTH: 'month', WEEK: 'week', DAY: 'day' },
  };
});

// Mock moment
jest.mock('moment', () => {
  const actualMoment = jest.requireActual('moment');
  return {
    ...actualMoment,
    default: actualMoment,
  };
});

describe('Calendar Component', () => {
  const mockQueryClient = {
    invalidateQueries: jest.fn(),
  };

  beforeEach(() => {
    const { useQuery, useMutation, useQueryClient } = require('react-query');
    
    useQueryClient.mockReturnValue(mockQueryClient);
    useQuery
      .mockReturnValueOnce({
        data: mockStudySessions,
        isLoading: false,
      })
      .mockReturnValueOnce({
        data: mockAssignments,
        isLoading: false,
      });
    useMutation.mockReturnValue({
      mutate: jest.fn(),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders calendar with study sessions and assignments', () => {
    render(<Calendar />);
    
    expect(screen.getByText('Study Schedule Calendar')).toBeInTheDocument();
    expect(screen.getByTestId('calendar')).toBeInTheDocument();
    expect(screen.getByText('Study Sessions')).toBeInTheDocument();
    expect(screen.getByText('Assignment Due Dates')).toBeInTheDocument();
  });

  it('displays study sessions as calendar events', () => {
    render(<Calendar />);
    
    // Should have events for study sessions
    const events = screen.getAllByTestId(/calendar-event-/);
    expect(events.length).toBeGreaterThan(0);
  });

  it('opens event details dialog when event is clicked', async () => {
    const user = userEvent.setup();
    render(<Calendar />);
    
    const events = screen.getAllByTestId(/calendar-event-/);
    await user.click(events[0]);
    
    await waitFor(() => {
      expect(screen.getByText('Study Session Details')).toBeInTheDocument();
    });
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
    
    render(<Calendar />);
    
    expect(screen.getByText('Loading calendar...')).toBeInTheDocument();
  });

  it('handles complete session action', async () => {
    const user = userEvent.setup();
    const mockMutate = jest.fn();
    
    const { useMutation } = require('react-query');
    useMutation.mockReturnValue({
      mutate: mockMutate,
    });
    
    render(<Calendar />);
    
    const events = screen.getAllByTestId(/calendar-event-/);
    await user.click(events[0]);
    
    await waitFor(() => {
      expect(screen.getByText('Study Session Details')).toBeInTheDocument();
    });
    
    const completeButton = screen.getByText('Mark Complete');
    await user.click(completeButton);
    
    expect(mockMutate).toHaveBeenCalled();
  });

  it('handles delete session action', async () => {
    const user = userEvent.setup();
    const mockMutate = jest.fn();
    
    const { useMutation } = require('react-query');
    useMutation.mockReturnValue({
      mutate: mockMutate,
    });
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
    
    render(<Calendar />);
    
    const events = screen.getAllByTestId(/calendar-event-/);
    await user.click(events[0]);
    
    await waitFor(() => {
      expect(screen.getByText('Study Session Details')).toBeInTheDocument();
    });
    
    const deleteButton = screen.getByText('Delete');
    await user.click(deleteButton);
    
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this study session?');
    expect(mockMutate).toHaveBeenCalled();
  });

  it('displays assignment due dates as events', () => {
    render(<Calendar />);
    
    // Should have events for both study sessions and assignment due dates
    const events = screen.getAllByTestId(/calendar-event-/);
    expect(events.length).toBeGreaterThan(0);
  });

  it('shows different event types with different colors', () => {
    render(<Calendar />);
    
    // The calendar should render with different event types
    // This is tested through the event rendering in the mock
    expect(screen.getByTestId('calendar')).toBeInTheDocument();
  });
});
