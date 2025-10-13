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
  Tabs,
  Tab,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  School,
  Bookmark,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import CourseSearch from '../components/CourseSearch';
import { useCourseCatalog } from '../hooks/useCourseCatalog';
import { CourseCatalog } from '../services/courseCatalogService';

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
  const [tabValue, setTabValue] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedCatalogCourses, setSelectedCatalogCourses] = useState<CourseCatalog[]>([]);
  const queryClient = useQueryClient();

  // Course catalog hook
  const {
    subjects,
    courses: catalogCourses,
    loadingSubjects,
    loadingCourses,
    error: catalogError,
    loadCourses,
    clearError: clearCatalogError,
  } = useCourseCatalog({ autoLoad: true });

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

  // Course catalog handlers
  const handleSubjectChange = (subject: string) => {
    setSelectedSubject(subject);
    if (subject) {
      loadCourses({ subject });
    }
  };

  const handleCatalogCourseAdd = (course: CourseCatalog) => {
    if (!selectedCatalogCourses.some(c => c.subject === course.subject && c.number === course.number)) {
      setSelectedCatalogCourses(prev => [...prev, course]);
      toast.success(`Added ${course.subject} ${course.number} to your courses!`);
    }
  };

  const handleCatalogCourseRemove = (course: CourseCatalog) => {
    setSelectedCatalogCourses(prev => 
      prev.filter(c => !(c.subject === course.subject && c.number === course.number))
    );
    toast.success(`Removed ${course.subject} ${course.number} from your courses.`);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
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
          Add Custom Course
        </Button>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="My Courses" />
          <Tab label="Course Catalog" />
          <Tab label="Search Courses" />
        </Tabs>
      </Box>

      {/* Tab 0: My Courses */}
      {tabValue === 0 && (
        <Box>
          <Grid container spacing={3}>
            {/* User's custom courses */}
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

            {/* Selected catalog courses */}
            {selectedCatalogCourses.map((course) => (
              <Grid item xs={12} sm={6} md={4} key={`${course.subject}-${course.number}`}>
                <Card sx={{ border: '2px solid', borderColor: 'primary.main' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Bookmark color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="div">
                        {course.subject} {course.number}
                      </Typography>
                    </Box>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      {course.title}
                    </Typography>
                    {course.credit_hours && (
                      <Chip 
                        label={`${course.credit_hours} credits`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                        sx={{ mb: 1 }}
                      />
                    )}
                    {course.description && (
                      <Typography variant="body2" color="textSecondary">
                        {course.description.substring(0, 100)}...
                      </Typography>
                    )}
                  </CardContent>
                  <CardActions>
                    <IconButton
                      size="small"
                      onClick={() => handleCatalogCourseRemove(course)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {(!courses || courses.length === 0) && selectedCatalogCourses.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary">
                No courses yet. Browse the course catalog or add a custom course to get started!
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Tab 1: Course Catalog */}
      {tabValue === 1 && (
        <Box>
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Subject</InputLabel>
              <Select
                value={selectedSubject}
                label="Select Subject"
                onChange={(e) => handleSubjectChange(e.target.value)}
                disabled={loadingSubjects}
              >
                {subjects.map((subject) => (
                  <MenuItem key={subject} value={subject}>
                    {subject}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {catalogError && (
              <Alert severity="error" onClose={clearCatalogError} sx={{ mb: 2 }}>
                {catalogError}
              </Alert>
            )}
          </Box>

          {selectedSubject && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {selectedSubject} Courses
                {loadingCourses && <CircularProgress size={20} sx={{ ml: 2 }} />}
              </Typography>
              
              <Grid container spacing={2}>
                {catalogCourses.map((course) => (
                  <Grid item xs={12} sm={6} md={4} key={`${course.subject}-${course.number}`}>
                    <Card>
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                          <Typography variant="h6">
                            {course.subject} {course.number}
                          </Typography>
                          {course.credit_hours && (
                            <Chip 
                              label={`${course.credit_hours} credits`} 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                          {course.title}
                        </Typography>
                        {course.description && (
                          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                            {course.description.substring(0, 150)}...
                          </Typography>
                        )}
                        {course.sections.length > 0 && (
                          <Box>
                            <Typography variant="caption" color="textSecondary">
                              {course.sections.length} sections available
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          startIcon={<Add />}
                          onClick={() => handleCatalogCourseAdd(course)}
                          disabled={selectedCatalogCourses.some(c => 
                            c.subject === course.subject && c.number === course.number
                          )}
                        >
                          {selectedCatalogCourses.some(c => 
                            c.subject === course.subject && c.number === course.number
                          ) ? 'Added' : 'Add Course'}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {catalogCourses.length === 0 && !loadingCourses && (
                <Box textAlign="center" py={4}>
                  <Typography variant="h6" color="textSecondary">
                    No courses found for {selectedSubject}
                  </Typography>
                </Box>
              )}
            </Box>
          )}

          {!selectedSubject && (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary">
                Select a subject to browse available courses
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Tab 2: Search Courses */}
      {tabValue === 2 && (
        <Box>
          <CourseSearch
            onCourseAdd={handleCatalogCourseAdd}
            selectedCourses={selectedCatalogCourses}
            placeholder="Search for courses (e.g., CS 225, MATH 241, Data Structures)"
            maxResults={20}
          />
        </Box>
      )}

      {/* Custom Course Dialog */}
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
