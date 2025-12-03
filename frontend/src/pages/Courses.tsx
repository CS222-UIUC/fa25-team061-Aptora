import React, { useState, useEffect } from 'react';
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
import { useAuth } from '../contexts/AuthContext';

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
  const [selectedCourseDetail, setSelectedCourseDetail] = useState<CourseCatalog | null>(null);
  const [courseDetailOpen, setCourseDetailOpen] = useState(false);

  const queryClient = useQueryClient();
  const { user } = useAuth();

  // Course catalog hook
  const {
    subjects,
    courses: catalogCourses,
    sections,
    loadingSubjects,
    loadingCourses,
    loadingSections,
    error: catalogError,
    loadCourses,
    loadSections,
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
    },
    {
      enabled: !!user, // Only fetch if user is authenticated
      refetchOnMount: true, // Refetch when component mounts
      refetchOnWindowFocus: true, // Refetch when window regains focus
      staleTime: 0, // Always consider data stale to ensure fresh data
    }
  );

  // Sync selectedCatalogCourses with backend courses on load
  useEffect(() => {
    if (courses && courses.length > 0) {
      // Filter out courses that are already in backend
      setSelectedCatalogCourses(prev => 
        prev.filter(catalogCourse => {
          const courseCode = `${catalogCourse.subject} ${catalogCourse.number}`;
          return !courses.some(backendCourse => backendCourse.code === courseCode);
        })
      );
    }
  }, [courses]);

  const createMutation = useMutation(
    async (data: FormData) => {
      if (!user) {
        throw new Error('You must be logged in to create courses');
      }
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
        toast.error(error.response?.data?.detail || error.message || 'Failed to create course');
      },
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: FormData }) => {
      if (!user) {
        throw new Error('You must be logged in to update courses');
      }
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
        toast.error(error.response?.data?.detail || error.message || 'Failed to update course');
      },
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      if (!user) {
        throw new Error('You must be logged in to delete courses');
      }
      await axios.delete(`/courses/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('courses');
        toast.success('Course deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || error.message || 'Failed to delete course');
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

  const handleCatalogCourseAdd = async (course: CourseCatalog) => {
    if (!user) {
      toast.error('Please log in to add courses');
      return;
    }

    // Check if course already exists in backend
    const courseCode = `${course.subject} ${course.number}`;
    const existingCourse = courses?.find(c => c.code === courseCode);
    
    if (existingCourse) {
      toast(`${courseCode} is already in your courses`);
      return;
    }

    // Check if already in selected catalog courses
    if (selectedCatalogCourses.some(c => c.subject === course.subject && c.number === course.number)) {
      toast(`${courseCode} is already in your courses`);
      return;
    }

    try {
      // Save to backend database
      const courseData: any = {
        name: course.title || `${course.subject} ${course.number}`,
        code: courseCode,
      };
      
      // Only include description if it exists
      if (course.description) {
        courseData.description = course.description;
      }
      
      await createMutation.mutateAsync(courseData);
      
      // Also add to selected catalog courses for UI consistency
      setSelectedCatalogCourses(prev => [...prev, course]);
      
      toast.success(`Added ${courseCode} to your courses!`);
    } catch (error: any) {
      // Don't add to local state if creation fails - show error instead
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save course to database';
      console.error('Error creating course:', error);
      toast.error(errorMessage);
      throw error; // Re-throw to prevent further processing
    }
  };

  const handleCatalogCourseRemove = async (course: CourseCatalog) => {
    if (!user) {
      toast.error('Please log in to remove courses');
      return;
    }

    const courseCode = `${course.subject} ${course.number}`;
    
    // Check if course exists in backend and delete it
    const existingCourse = courses?.find(c => c.code === courseCode);
    if (existingCourse) {
      try {
        await deleteMutation.mutateAsync(existingCourse.id);
        toast.success(`Removed ${courseCode} from your courses.`);
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to remove course from database');
      }
    } else {
      // If not in backend, just remove from local state
      setSelectedCatalogCourses(prev => 
        prev.filter(c => !(c.subject === course.subject && c.number === course.number))
      );
      toast.success(`Removed ${courseCode} from your courses.`);
    }
  };

  const handleCourseDetailOpen = async (course: CourseCatalog) => {
    setSelectedCourseDetail(course);
    setCourseDetailOpen(true);
    // Load sections for this course
    await loadSections(course.subject, course.number);
  };

  const handleCourseDetailClose = () => {
    setCourseDetailOpen(false);
    setSelectedCourseDetail(null);
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
          disabled={!user}
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
          {!user ? (
            <Alert severity="info" sx={{ mb: 3 }}>
              Please log in to view and manage your personal courses.
            </Alert>
          ) : (
            <>
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
            </>
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
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: 3,
                        }
                      }}
                      onClick={() => handleCourseDetailOpen(course)}
                    >
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
                        <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block' }}>
                          Click to view details and sections
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          startIcon={<Add />}
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent card click
                            handleCatalogCourseAdd(course);
                          }}
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
            onCourseSelect={handleCourseDetailOpen}
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

      {/* Course Detail Dialog */}
      <Dialog 
        open={courseDetailOpen} 
        onClose={handleCourseDetailClose} 
        maxWidth="md" 
        fullWidth
      >
        {selectedCourseDetail && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h5" component="div">
                    {selectedCourseDetail.subject} {selectedCourseDetail.number}
                  </Typography>
                  <Typography variant="subtitle1" color="textSecondary">
                    {selectedCourseDetail.title}
                  </Typography>
                </Box>
                {selectedCourseDetail.credit_hours && (
                  <Chip 
                    label={`${selectedCourseDetail.credit_hours} credits`} 
                    color="primary" 
                    variant="outlined"
                  />
                )}
              </Box>
            </DialogTitle>
            
            <DialogContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Course Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Subject:</strong> {selectedCourseDetail.subject}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Course Number:</strong> {selectedCourseDetail.number}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Semester:</strong> {selectedCourseDetail.semester}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">
                      <strong>Year:</strong> {selectedCourseDetail.year}
                    </Typography>
                  </Grid>
                  {selectedCourseDetail.credit_hours && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        <strong>Credit Hours:</strong> {selectedCourseDetail.credit_hours}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>

              {selectedCourseDetail.description && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Description
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {selectedCourseDetail.description}
                  </Typography>
                </Box>
              )}

              <Box>
                <Typography variant="h6" gutterBottom>
                  Available Sections
                  {loadingSections && <CircularProgress size={20} sx={{ ml: 2 }} />}
                </Typography>
                
                {sections.length > 0 ? (
                  <Grid container spacing={2}>
                    {sections.map((section) => (
                      <Grid item xs={12} sm={6} md={4} key={section.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="subtitle1" gutterBottom>
                              Section {section.crn}
                            </Typography>
                            {section.days && (
                              <Typography variant="body2" color="textSecondary">
                                <strong>Days:</strong> {section.days}
                              </Typography>
                            )}
                            {section.times && (
                              <Typography variant="body2" color="textSecondary">
                                <strong>Time:</strong> {section.times}
                              </Typography>
                            )}
                            {section.instructor && (
                              <Typography variant="body2" color="textSecondary">
                                <strong>Instructor:</strong> {section.instructor}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    No sections available for this course.
                  </Typography>
                )}
              </Box>
            </DialogContent>
            
            <DialogActions>
              <Button onClick={handleCourseDetailClose}>Close</Button>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => {
                  handleCatalogCourseAdd(selectedCourseDetail);
                  handleCourseDetailClose();
                }}
                disabled={selectedCatalogCourses.some(c => 
                  c.subject === selectedCourseDetail.subject && c.number === selectedCourseDetail.number
                )}
              >
                {selectedCatalogCourses.some(c => 
                  c.subject === selectedCourseDetail.subject && c.number === selectedCourseDetail.number
                ) ? 'Already Added' : 'Add to My Courses'}
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default Courses;
