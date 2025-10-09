import React from 'react';
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
} from '@mui/material';
import {
  Assignment,
  Schedule,
  School,
  TrendingUp,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

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

  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    async () => {
      const response = await axios.get('/dashboard/stats');
      return response.data;
    }
  );

  const { data: upcomingAssignments, isLoading: assignmentsLoading } = useQuery<UpcomingAssignment[]>(
    'upcoming-assignments',
    async () => {
      const response = await axios.get('/assignments/upcoming');
      return response.data;
    }
  );

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  if (statsLoading || assignmentsLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <School color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Courses
                  </Typography>
                  <Typography variant="h4">
                    {stats?.total_courses || 0}
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

        {/* Upcoming Assignments */}
        <Grid item xs={12} md={8}>
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
                Add Course
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
                startIcon={<Schedule />}
              >
                Set Availability
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
