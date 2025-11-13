import React, { useMemo, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Chip,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { Add, Delete, Edit } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

const priorities = ['high', 'medium', 'low'] as const;

const schema = yup.object({
  title: yup.string().required('Task title is required'),
  description: yup.string(),
  due_date: yup
    .date()
    .required('Due date is required')
    .typeError('Due date is required')
    .test('future-date', 'Due date must be in the future', (value) =>
      value ? dayjs(value).isAfter(dayjs()) : false
    ),
  estimated_hours: yup
    .number()
    .positive('Hours must be positive')
    .required('Estimated hours is required'),
  difficulty: yup
    .string()
    .oneOf(['easy', 'medium', 'hard'])
    .required('Difficulty is required'),
  task_type: yup
    .string()
    .oneOf(['assignment', 'exam', 'project'])
    .required('Task type is required'),
  priority: yup
    .string()
    .oneOf(priorities as unknown as string[])
    .required('Priority is required'),
  course_id: yup
    .number()
    .typeError('Course is required')
    .required('Course is required'),
});

type FormData = yup.InferType<typeof schema>;

interface Assignment {
  id: number;
  title: string;
  description?: string;
  due_date: string;
  estimated_hours: number;
  difficulty: 'easy' | 'medium' | 'hard';
  task_type: 'assignment' | 'exam' | 'project';
  course_id: number;
  priority: 'high' | 'medium' | 'low';
  is_completed: boolean;
}

interface Course {
  id: number;
  name: string;
  code: string;
}

const Assignments: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<Assignment | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<string>('all');
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const [dueBefore, setDueBefore] = useState<Date | null>(null);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      title: '',
      description: '',
      due_date: undefined,
      estimated_hours: 1,
      difficulty: 'medium',
      task_type: 'assignment',
      priority: 'medium',
      course_id: undefined,
    },
  });

  const { data: courses } = useQuery<Course[]>('courses', async () => {
    const response = await axios.get('/courses/');
    return response.data;
  });

  const { data: assignments, isLoading } = useQuery<Assignment[]>(
    ['assignments', selectedCourse, selectedPriority, dueBefore?.toISOString()],
    async () => {
      const params: Record<string, string> = {};
      if (selectedCourse !== 'all') {
        params.course_id = selectedCourse;
      }
      if (selectedPriority !== 'all') {
        params.priority = selectedPriority;
      }
      if (dueBefore) {
        params.due_before = dueBefore.toISOString();
      }
      const response = await axios.get('/assignments/', { params });
      return response.data;
    }
  );

  const courseNameById = useMemo(() => {
    const map = new Map<number, string>();
    courses?.forEach((course) => {
      map.set(course.id, `${course.name} (${course.code})`);
    });
    return map;
  }, [courses]);

  const createMutation = useMutation(
    async (data: FormData) => {
      const response = await axios.post('/assignments/', {
        ...data,
        due_date: data.due_date.toISOString(),
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Task created successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create task');
      },
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: FormData }) => {
      const response = await axios.put(`/assignments/${id}`, {
        ...data,
        due_date: data.due_date.toISOString(),
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Task updated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update task');
      },
    }
  );

  const completionToggleMutation = useMutation(
    async ({ id, is_completed }: { id: number; is_completed: boolean }) => {
      const response = await axios.put(`/assignments/${id}`, {
        is_completed,
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Task status updated!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update task status');
      },
    }
  );

  const completeMutation = useMutation(
    async (id: number) => {
      const response = await axios.patch(`/assignments/${id}/complete`);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Task marked as complete!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to mark task as complete');
      },
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      await axios.delete(`/assignments/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Task deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete task');
      },
    }
  );

  const handleOpen = () => {
    setEditingAssignment(null);
    reset();
    setOpen(true);
  };

  const handleEdit = (assignment: Assignment) => {
    setEditingAssignment(assignment);
    reset({
      title: assignment.title,
      description: assignment.description || '',
      due_date: new Date(assignment.due_date),
      estimated_hours: assignment.estimated_hours,
      difficulty: assignment.difficulty,
      task_type: assignment.task_type,
      priority: assignment.priority,
      course_id: assignment.course_id,
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingAssignment(null);
    reset();
  };

  const onSubmit = (data: FormData) => {
    if (editingAssignment) {
      updateMutation.mutate({ id: editingAssignment.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleCompletionChange = (assignment: Assignment, checked: boolean) => {
    if (checked) {
      completeMutation.mutate(assignment.id);
    } else {
      completionToggleMutation.mutate({
        id: assignment.id,
        is_completed: false,
      });
    }
  };

  const handleClearFilters = () => {
    setSelectedCourse('all');
    setSelectedPriority('all');
    setDueBefore(null);
  };

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Tasks</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleOpen}>
          Add Task
        </Button>
      </Box>

      <Box
        display="flex"
        flexWrap="wrap"
        gap={2}
        alignItems="center"
        mb={3}
      >
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Course</InputLabel>
          <Select
            label="Course"
            value={selectedCourse}
            onChange={(event) => setSelectedCourse(event.target.value)}
          >
            <MenuItem value="all">All Courses</MenuItem>
            {courses?.map((course) => (
              <MenuItem key={course.id} value={course.id.toString()}>
                {course.name} ({course.code})
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 160 }}>
          <InputLabel>Priority</InputLabel>
          <Select
            label="Priority"
            value={selectedPriority}
            onChange={(event) => setSelectedPriority(event.target.value)}
          >
            <MenuItem value="all">All Priorities</MenuItem>
            {priorities.map((priority) => (
              <MenuItem key={priority} value={priority}>
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DatePicker
            label="Due Before"
            value={dueBefore ? dayjs(dueBefore) : null}
            onChange={(date) => setDueBefore(date ? date.toDate() : null)}
            slotProps={{
              textField: {
                sx: { minWidth: 180 },
              },
            }}
          />
        </LocalizationProvider>

        <Button onClick={handleClearFilters}>Clear Filters</Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell align="center">Done</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Course</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading && (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography align="center" py={3}>
                    Loading tasks...
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {!isLoading && (!assignments || assignments.length === 0) && (
              <TableRow>
                <TableCell colSpan={6}>
                  <Typography align="center" py={3} color="text.secondary">
                    No tasks yet. Add your first task to get started!
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {assignments?.map((assignment) => (
              <TableRow
                key={assignment.id}
                sx={{
                  opacity: assignment.is_completed ? 0.7 : 1,
                }}
              >
                <TableCell align="center">
                  <Checkbox
                    checked={assignment.is_completed}
                    onChange={(event) =>
                      handleCompletionChange(assignment, event.target.checked)
                    }
                    color="success"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle1">{assignment.title}</Typography>
                  {assignment.description && (
                    <Typography variant="body2" color="text.secondary">
                      {assignment.description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {courseNameById.get(assignment.course_id) || '—'}
                </TableCell>
                <TableCell>
                  {new Date(assignment.due_date).toLocaleString()}
                </TableCell>
                <TableCell>
                  <Chip
                    label={assignment.priority}
                    color={
                      assignment.priority === 'high'
                        ? 'error'
                        : assignment.priority === 'medium'
                        ? 'warning'
                        : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleEdit(assignment)}
                    aria-label="edit"
                    sx={{ mr: 1 }}
                  >
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(assignment.id)}
                    aria-label="delete"
                  >
                    <Delete fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingAssignment ? 'Edit Task' : 'Add New Task'}</DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Title"
              fullWidth
              variant="outlined"
              {...register('title')}
              error={!!errors.title}
              helperText={errors.title?.message}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              {...register('description')}
              error={!!errors.description}
              helperText={errors.description?.message}
              sx={{ mb: 2 }}
            />
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <Controller
                name="due_date"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    label="Due Date"
                    value={field.value ? dayjs(field.value) : null}
                    onChange={(date) => field.onChange(date?.toDate())}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'dense',
                        error: !!errors.due_date,
                        helperText: errors.due_date?.message,
                        sx: { mb: 2 },
                      },
                    }}
                  />
                )}
              />
            </LocalizationProvider>
            <TextField
              margin="dense"
              label="Estimated Hours"
              type="number"
              fullWidth
              variant="outlined"
              {...register('estimated_hours', { valueAsNumber: true })}
              error={!!errors.estimated_hours}
              helperText={errors.estimated_hours?.message}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel>Course</InputLabel>
              <Select
                label="Course"
                defaultValue=""
                {...register('course_id', { valueAsNumber: true })}
                error={!!errors.course_id}
              >
                {courses?.map((course) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.name} ({course.code})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel>Priority</InputLabel>
              <Select
                label="Priority"
                defaultValue="medium"
                {...register('priority')}
                error={!!errors.priority}
              >
                {priorities.map((priority) => (
                  <MenuItem key={priority} value={priority}>
                    {priority.charAt(0).toUpperCase() + priority.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel>Difficulty</InputLabel>
              <Select
                label="Difficulty"
                defaultValue="medium"
                {...register('difficulty')}
                error={!!errors.difficulty}
              >
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Task Type</InputLabel>
              <Select
                label="Task Type"
                defaultValue="assignment"
                {...register('task_type')}
                error={!!errors.task_type}
              >
                <MenuItem value="assignment">Assignment</MenuItem>
                <MenuItem value="exam">Exam</MenuItem>
                <MenuItem value="project">Project</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : editingAssignment ? 'Update Task' : 'Create Task'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default Assignments;
