import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  Avatar,
} from '@mui/material';
import {
  Assignment,
  Schedule,
  School,
  TrendingUp,
  Add,
  AccessTime,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { CourseCatalog } from '../services/courseCatalogService';

interface DashboardStats {
  total_courses: number;
  total_assignments: number;
  upcoming_assignments: number;
  completed_sessions: number;
}

interface UpcomingAssignment {
  id: number;
  title: string;
  due_date: string;
  course_name: string;
  difficulty: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [selectedCatalogCourses, setSelectedCatalogCourses] = useState<CourseCatalog[]>([]);

  // Load selected courses from localStorage on component mount
  useEffect(() => {
    const savedCourses = localStorage.getItem('selectedCatalogCourses');
    if (savedCourses) {
      try {
        setSelectedCatalogCourses(JSON.parse(savedCourses));
      } catch (error) {
        console.error('Error parsing saved courses:', error);
      }
    }
  }, []);

  // Listen for storage changes (when courses are updated in other tabs/components)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'selectedCatalogCourses' && e.newValue) {
        try {
          setSelectedCatalogCourses(JSON.parse(e.newValue));
        } catch (error) {
          console.error('Error parsing updated courses:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Mock data for now - we'll implement real backend endpoints later
  const stats: DashboardStats = {
    total_courses: selectedCatalogCourses.length,
    total_assignments: 0,
    upcoming_assignments: 0,
    completed_sessions: 0,
  };

  const upcomingAssignments: UpcomingAssignment[] = [];
  const statsLoading = false;
  const assignmentsLoading = false;

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  // Remove loading check since we're using mock data

  try {
    return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Dashboard
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Welcome back! Here's your study overview.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <School color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    My Courses
                  </Typography>
                  <Typography variant="h4">
                    {selectedCatalogCourses.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assignment color="secondary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Assignments
                  </Typography>
                  <Typography variant="h4">
                    {stats?.total_assignments || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Schedule color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Upcoming
                  </Typography>
                  <Typography variant="h4">
                    {stats?.upcoming_assignments || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completed Sessions
                  </Typography>
                  <Typography variant="h4">
                    {stats?.completed_sessions || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* My Current Courses */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">My Current Courses</Typography>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => navigate('/courses')}
              >
                Add Courses
              </Button>
            </Box>
            {selectedCatalogCourses.length > 0 ? (
              <Grid container spacing={2}>
                {selectedCatalogCourses.slice(0, 6).map((course: CourseCatalog) => (
                  <Grid item xs={12} sm={6} md={4} key={`${course.subject}-${course.number}`}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={1}>
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, mr: 1 }}>
                            {course.subject.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {course.subject} {course.number}
                            </Typography>
                            <Typography 
                              variant="body2" 
                              color="textSecondary"
                              sx={{
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                hyphens: 'auto',
                                lineHeight: 1.3,
                                maxHeight: '2.6em', // Allow for 2 lines
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {course.title}
                            </Typography>
                          </Box>
                        </Box>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Chip
                            label={course.semester}
                            size="small"
                            variant="outlined"
                          />
                          {course.credit_hours && (
                            <Typography variant="caption" color="textSecondary">
                              {course.credit_hours} credits
                            </Typography>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box textAlign="center" py={4}>
                <School sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No courses selected yet
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Start by adding courses from the course catalog to get personalized study recommendations.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => navigate('/courses')}
                >
                  Browse Course Catalog
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Button
                variant="contained"
                onClick={() => navigate('/courses')}
                startIcon={<School />}
              >
                Browse Course Catalog
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/assignments')}
                startIcon={<Assignment />}
              >
                Add Assignment
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/schedule')}
                startIcon={<Schedule />}
              >
                Generate Schedule
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/availability')}
                startIcon={<AccessTime />}
              >
                Set Availability
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Upcoming Assignments */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Upcoming Assignments</Typography>
              <Button
                variant="outlined"
                onClick={() => navigate('/assignments')}
              >
                View All
              </Button>
            </Box>
            <List>
              {upcomingAssignments?.slice(0, 5).map((assignment) => (
                <ListItem key={assignment.id} divider>
                  <ListItemText
                    primary={assignment.title}
                    secondary={`${assignment.course_name} • Due: ${new Date(assignment.due_date).toLocaleDateString()}`}
                  />
                  <Chip
                    label={assignment.difficulty}
                    color={getDifficultyColor(assignment.difficulty) as any}
                    size="small"
                  />
                </ListItem>
              ))}
              {(!upcomingAssignments || upcomingAssignments.length === 0) && (
                <ListItem>
                  <ListItemText primary="No upcoming assignments" />
                </ListItem>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
    );
  } catch (error) {
    console.error('Dashboard render error:', error);
    return (
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="error">
          Something went wrong loading the dashboard. Please try refreshing the page.
        </Typography>
      </Container>
    );
  }
};

export default Dashboard;
