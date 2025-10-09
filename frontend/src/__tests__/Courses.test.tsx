import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../utils/testUtils';
import Courses from '../pages/Courses';
import { mockCourses } from '../utils/mockData';

// Mock react-query
jest.mock('react-query', () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(),
  useQueryClient: jest.fn(),
}));

// Mock axios
jest.mock('axios');
const mockAxios = require('axios');

describe('Courses Component', () => {
  const mockQueryClient = {
    invalidateQueries: jest.fn(),
  };

  beforeEach(() => {
    const { useQuery, useMutation, useQueryClient } = require('react-query');
    
    useQueryClient.mockReturnValue(mockQueryClient);
    useQuery.mockReturnValue({
      data: mockCourses,
      isLoading: false,
    });
    useMutation.mockReturnValue({
      mutate: jest.fn(),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders courses list correctly', () => {
    render(<Courses />);
    
    expect(screen.getByText('Courses')).toBeInTheDocument();
    expect(screen.getByText('Add Course')).toBeInTheDocument();
    expect(screen.getByText('Data Structures and Algorithms')).toBeInTheDocument();
    expect(screen.getByText('CS 222')).toBeInTheDocument();
    expect(screen.getByText('Software Engineering')).toBeInTheDocument();
    expect(screen.getByText('CS 333')).toBeInTheDocument();
  });

  it('opens add course dialog when Add Course button is clicked', async () => {
    const user = userEvent.setup();
    render(<Courses />);
    
    const addButton = screen.getByText('Add Course');
    await user.click(addButton);
    
    expect(screen.getByText('Add New Course')).toBeInTheDocument();
    expect(screen.getByLabelText('Course Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Course Code')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
  });

  it('opens edit course dialog when edit button is clicked', async () => {
    const user = userEvent.setup();
    render(<Courses />);
    
    const editButtons = screen.getAllByTestId('EditIcon');
    await user.click(editButtons[0]);
    
    expect(screen.getByText('Edit Course')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Data Structures and Algorithms')).toBeInTheDocument();
    expect(screen.getByDisplayValue('CS 222')).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    render(<Courses />);
    
    const addButton = screen.getByText('Add Course');
    await user.click(addButton);
    
    const createButton = screen.getByText('Create');
    await user.click(createButton);
    
    await waitFor(() => {
      expect(screen.getByText('Course name is required')).toBeInTheDocument();
      expect(screen.getByText('Course code is required')).toBeInTheDocument();
    });
  });

  it('calls create course API when form is submitted with valid data', async () => {
    const user = userEvent.setup();
    const mockMutate = jest.fn();
    
    const { useMutation } = require('react-query');
    useMutation.mockReturnValue({
      mutate: mockMutate,
    });
    
    render(<Courses />);
    
    const addButton = screen.getByText('Add Course');
    await user.click(addButton);
    
    const courseNameInput = screen.getByLabelText('Course Name');
    const courseCodeInput = screen.getByLabelText('Course Code');
    const descriptionInput = screen.getByLabelText('Description');
    const createButton = screen.getByText('Create');
    
    await user.type(courseNameInput, 'Test Course');
    await user.type(courseCodeInput, 'TEST 101');
    await user.type(descriptionInput, 'Test Description');
    await user.click(createButton);
    
    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith({
        name: 'Test Course',
        code: 'TEST 101',
        description: 'Test Description',
      });
    });
  });

  it('shows loading state when courses are being fetched', () => {
    const { useQuery } = require('react-query');
    useQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    
    render(<Courses />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no courses exist', () => {
    const { useQuery } = require('react-query');
    useQuery.mockReturnValue({
      data: [],
      isLoading: false,
    });
    
    render(<Courses />);
    
    expect(screen.getByText('No courses yet. Add your first course to get started!')).toBeInTheDocument();
  });

  it('calls delete course API when delete button is clicked', async () => {
    const user = userEvent.setup();
    const mockMutate = jest.fn();
    
    const { useMutation } = require('react-query');
    useMutation.mockReturnValue({
      mutate: mockMutate,
    });
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
    
    render(<Courses />);
    
    const deleteButtons = screen.getAllByTestId('DeleteIcon');
    await user.click(deleteButtons[0]);
    
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this course?');
    expect(mockMutate).toHaveBeenCalledWith(1); // First course ID
  });
});
