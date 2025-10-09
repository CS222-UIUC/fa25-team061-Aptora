import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Grid,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Assignment,
  CheckCircle,
} from '@mui/icons-material';
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

const schema = yup.object({
  title: yup.string().required('Assignment title is required'),
  description: yup.string(),
  due_date: yup.date().required('Due date is required'),
  estimated_hours: yup.number().positive('Hours must be positive').required('Estimated hours is required'),
  difficulty: yup.string().oneOf(['easy', 'medium', 'hard']).required('Difficulty is required'),
  task_type: yup.string().oneOf(['assignment', 'exam', 'project']).required('Task type is required'),
  course_id: yup.number().required('Course is required'),
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
  course_name?: string;
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
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  });

  const { data: assignments, isLoading } = useQuery<Assignment[]>(
    'assignments',
    async () => {
      const response = await axios.get('/assignments/');
      return response.data;
    }
  );

  const { data: courses } = useQuery<Course[]>(
    'courses',
    async () => {
      const response = await axios.get('/courses/');
      return response.data;
    }
  );

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
        toast.success('Assignment created successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create assignment');
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
        toast.success('Assignment updated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update assignment');
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
        toast.success('Assignment deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete assignment');
      },
    }
  );

  const completeMutation = useMutation(
    async (id: number) => {
      await axios.patch(`/assignments/${id}/complete`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assignments');
        toast.success('Assignment marked as completed!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to mark assignment as completed');
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
      course_id: assignment.course_id,
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingAssignment(null);
    reset();
  };

  const onSubmit = async (data: FormData) => {
    if (editingAssignment) {
      updateMutation.mutate({ id: editingAssignment.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this assignment?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleComplete = (id: number) => {
    completeMutation.mutate(id);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getTaskTypeColor = (taskType: string) => {
    switch (taskType) {
      case 'assignment': return 'primary';
      case 'exam': return 'secondary';
      case 'project': return 'info';
      default: return 'default';
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Assignments</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpen}
        >
          Add Assignment
        </Button>
      </Box>

      <Grid container spacing={3}>
        {assignments?.map((assignment) => (
          <Grid item xs={12} sm={6} md={4} key={assignment.id}>
            <Card sx={{ opacity: assignment.is_completed ? 0.7 : 1 }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Assignment color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {assignment.title}
                  </Typography>
                  {assignment.is_completed && (
                    <CheckCircle color="success" sx={{ ml: 1 }} />
                  )}
                </Box>
                <Typography color="textSecondary" gutterBottom>
                  Due: {new Date(assignment.due_date).toLocaleDateString()}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {assignment.estimated_hours} hours estimated
                </Typography>
                {assignment.description && (
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    {assignment.description}
                  </Typography>
                )}
                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip
                    label={assignment.difficulty}
                    color={getDifficultyColor(assignment.difficulty) as any}
                    size="small"
                  />
                  <Chip
                    label={assignment.task_type}
                    color={getTaskTypeColor(assignment.task_type) as any}
                    size="small"
                  />
                </Box>
              </CardContent>
              <CardActions>
                {!assignment.is_completed && (
                  <Button
                    size="small"
                    onClick={() => handleComplete(assignment.id)}
                    startIcon={<CheckCircle />}
                  >
                    Complete
                  </Button>
                )}
                <IconButton
                  size="small"
                  onClick={() => handleEdit(assignment)}
                >
                  <Edit />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDelete(assignment.id)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {(!assignments || assignments.length === 0) && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="textSecondary">
            No assignments yet. Add your first assignment to get started!
          </Typography>
        </Box>
      )}

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingAssignment ? 'Edit Assignment' : 'Add New Assignment'}
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Assignment Title"
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
                        sx: { mb: 2 }
                      }
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
              <InputLabel>Difficulty</InputLabel>
              <Select
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
            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : editingAssignment ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default Assignments;
