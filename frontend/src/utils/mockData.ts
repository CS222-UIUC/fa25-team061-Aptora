// Mock data for testing and development

export const mockUser = {
  id: 1,
  email: 'test@example.com',
  first_name: 'John',
  last_name: 'Doe',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockCourses = [
  {
    id: 1,
    name: 'Data Structures and Algorithms',
    code: 'CS 222',
    description: 'Advanced data structures and algorithm analysis',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Software Engineering',
    code: 'CS 333',
    description: 'Software development methodologies and practices',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

export const mockAssignments = [
  {
    id: 1,
    title: 'Binary Search Tree Implementation',
    description: 'Implement a balanced BST with insert, delete, and search operations',
    due_date: '2024-02-15T23:59:59Z',
    estimated_hours: 8,
    difficulty: 'hard' as const,
    task_type: 'assignment' as const,
    course_id: 1,
    is_completed: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'Midterm Exam',
    description: 'Comprehensive exam covering algorithms and data structures',
    due_date: '2024-02-20T14:00:00Z',
    estimated_hours: 3,
    difficulty: 'hard' as const,
    task_type: 'exam' as const,
    course_id: 1,
    is_completed: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    title: 'Project Proposal',
    description: 'Submit a detailed proposal for the final project',
    due_date: '2024-02-10T23:59:59Z',
    estimated_hours: 4,
    difficulty: 'medium' as const,
    task_type: 'project' as const,
    course_id: 2,
    is_completed: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

export const mockAvailabilitySlots = [
  {
    id: 1,
    day_of_week: 1, // Tuesday
    start_time: '09:00',
    end_time: '12:00',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    day_of_week: 3, // Thursday
    start_time: '14:00',
    end_time: '18:00',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    day_of_week: 5, // Saturday
    start_time: '10:00',
    end_time: '16:00',
    user_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

export const mockStudySessions = [
  {
    id: 1,
    start_time: '2024-02-12T09:00:00Z',
    end_time: '2024-02-12T11:00:00Z',
    is_completed: false,
    notes: 'Focus on BST implementation',
    user_id: 1,
    assignment_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    start_time: '2024-02-13T14:00:00Z',
    end_time: '2024-02-13T16:00:00Z',
    is_completed: true,
    notes: 'Completed project proposal review',
    user_id: 1,
    assignment_id: 3,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

export const mockDashboardStats = {
  total_courses: 2,
  total_assignments: 3,
  upcoming_assignments: 2,
  completed_sessions: 1,
};

export const mockUpcomingAssignments = [
  {
    id: 1,
    title: 'Binary Search Tree Implementation',
    due_date: '2024-02-15T23:59:59Z',
    course_name: 'Data Structures and Algorithms',
    difficulty: 'hard',
  },
  {
    id: 2,
    title: 'Midterm Exam',
    due_date: '2024-02-20T14:00:00Z',
    course_name: 'Data Structures and Algorithms',
    difficulty: 'hard',
  },
];
