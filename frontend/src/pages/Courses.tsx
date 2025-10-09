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
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  School,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const schema = yup.object({
  name: yup.string().required('Course name is required'),
  code: yup.string().required('Course code is required'),
  description: yup.string(),
});

type FormData = yup.InferType<typeof schema>;

interface Course {
  id: number;
  name: string;
  code: string;
  description?: string;
  created_at: string;
}

const Courses: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  });

  const { data: courses, isLoading } = useQuery<Course[]>(
    'courses',
    async () => {
      const response = await axios.get('/courses/');
      return response.data;
    }
  );

  const createMutation = useMutation(
    async (data: FormData) => {
      const response = await axios.post('/courses/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
        toast.success('Course created successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create course');
      },
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: FormData }) => {
      const response = await axios.put(`/courses/${id}`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
        toast.success('Course updated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update course');
      },
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      await axios.delete(`/courses/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
        toast.success('Course deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete course');
      },
    }
  );

  const handleOpen = () => {
    setEditingCourse(null);
    reset();
    setOpen(true);
  };

  const handleEdit = (course: Course) => {
    setEditingCourse(course);
    reset({
      name: course.name,
      code: course.code,
      description: course.description || '',
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingCourse(null);
    reset();
  };

  const onSubmit = async (data: FormData) => {
    if (editingCourse) {
      updateMutation.mutate({ id: editingCourse.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Courses</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpen}
        >
          Add Course
        </Button>
      </Box>

      <Grid container spacing={3}>
        {courses?.map((course) => (
          <Grid item xs={12} sm={6} md={4} key={course.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <School color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {course.name}
                  </Typography>
                </Box>
                <Typography color="textSecondary" gutterBottom>
                  {course.code}
                </Typography>
                {course.description && (
                  <Typography variant="body2" color="textSecondary">
                    {course.description}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <IconButton
                  size="small"
                  onClick={() => handleEdit(course)}
                >
                  <Edit />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDelete(course.id)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {(!courses || courses.length === 0) && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="textSecondary">
            No courses yet. Add your first course to get started!
          </Typography>
        </Box>
      )}

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingCourse ? 'Edit Course' : 'Add New Course'}
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Course Name"
              fullWidth
              variant="outlined"
              {...register('name')}
              error={!!errors.name}
              helperText={errors.name?.message}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Course Code"
              fullWidth
              variant="outlined"
              {...register('code')}
              error={!!errors.code}
              helperText={errors.code?.message}
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
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : editingCourse ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default Courses;
