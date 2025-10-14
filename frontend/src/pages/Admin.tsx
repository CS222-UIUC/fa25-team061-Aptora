import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh,
  PlayArrow,
  Stop,
  Info,
  Schedule,
  School,
  TrendingUp,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';

interface SystemStatus {
  status: string;
  timestamp: string;
  database: {
    total_courses: number;
    total_sections: number;
    unique_subjects: number;
    last_updated: string | null;
  };
  scheduler: {
    status: string;
    jobs: Array<{
      id: string;
      name: string;
      next_run: string | null;
      trigger: string;
    }>;
  };
}

interface CourseStats {
  top_subjects: Array<{ subject: string; count: number }>;
  by_semester: Array<{ semester: string; year: number; count: number }>;
  courses_with_sections: number;
  total_courses: number;
  total_sections: number;
}

const Admin: React.FC = () => {
  const queryClient = useQueryClient();

  // Fetch system status
  const { data: systemStatus, isLoading: statusLoading, refetch: refetchStatus } = useQuery<SystemStatus>(
    'systemStatus',
    async () => {
      const response = await fetch('/admin/status');
      if (!response.ok) throw new Error('Failed to fetch system status');
      return response.json();
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // Fetch course statistics
  const { data: courseStats, isLoading: statsLoading } = useQuery<CourseStats>(
    'courseStats',
    async () => {
      const response = await fetch('/admin/courses/stats');
      if (!response.ok) throw new Error('Failed to fetch course statistics');
      return response.json();
    }
  );

  // Refresh courses mutation
  const refreshCoursesMutation = useMutation(
    async () => {
      const response = await fetch('/admin/refresh-courses', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to refresh courses');
      return response.json();
    },
    {
      onSuccess: () => {
        toast.success('Course data refresh started successfully!');
        queryClient.invalidateQueries('systemStatus');
        queryClient.invalidateQueries('courseStats');
      },
      onError: (error: any) => {
        toast.error(error.message || 'Failed to refresh courses');
      },
    }
  );

  // Scheduler control mutations
  const startSchedulerMutation = useMutation(
    async () => {
      const response = await fetch('/admin/scheduler/start', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to start scheduler');
      return response.json();
    },
    {
      onSuccess: () => {
        toast.success('Scheduler started successfully!');
        refetchStatus();
      },
      onError: (error: any) => {
        toast.error(error.message || 'Failed to start scheduler');
      },
    }
  );

  const stopSchedulerMutation = useMutation(
    async () => {
      const response = await fetch('/admin/scheduler/stop', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to stop scheduler');
      return response.json();
    },
    {
      onSuccess: () => {
        toast.success('Scheduler stopped successfully!');
        refetchStatus();
      },
      onError: (error: any) => {
        toast.error(error.message || 'Failed to stop scheduler');
      },
    }
  );

  const handleRefreshCourses = () => {
    refreshCoursesMutation.mutate();
  };

  const handleStartScheduler = () => {
    startSchedulerMutation.mutate();
  };

  const handleStopScheduler = () => {
    stopSchedulerMutation.mutate();
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const formatNextRun = (nextRun: string | null) => {
    if (!nextRun) return 'Not scheduled';
    return new Date(nextRun).toLocaleString();
  };

  if (statusLoading || statsLoading) {
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
        <Typography variant="h4">System Administration</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => {
              refetchStatus();
              queryClient.invalidateQueries('courseStats');
            }}
            sx={{ mr: 1 }}
          >
            Refresh Status
          </Button>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={handleRefreshCourses}
            disabled={refreshCoursesMutation.isLoading}
          >
            {refreshCoursesMutation.isLoading ? 'Refreshing...' : 'Refresh Course Data'}
          </Button>
        </Box>
      </Box>

      {/* System Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Info color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={2}>
                <Chip
                  label={systemStatus?.status || 'Unknown'}
                  color={systemStatus?.status === 'healthy' ? 'success' : 'error'}
                  sx={{ mr: 2 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Last checked: {formatDate(systemStatus?.timestamp)}
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Database: {systemStatus?.database.total_courses || 0} courses, {systemStatus?.database.total_sections || 0} sections
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last updated: {formatDate(systemStatus?.database.last_updated)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Schedule color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Scheduler</Typography>
              </Box>
              <Box display="flex" alignItems="center" mb={2}>
                <Chip
                  label={systemStatus?.scheduler.status || 'Unknown'}
                  color={systemStatus?.scheduler.status === 'running' ? 'success' : 'default'}
                  sx={{ mr: 2 }}
                />
                <Tooltip title="Start Scheduler">
                  <IconButton
                    size="small"
                    onClick={handleStartScheduler}
                    disabled={startSchedulerMutation.isLoading || systemStatus?.scheduler.status === 'running'}
                  >
                    <PlayArrow />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Stop Scheduler">
                  <IconButton
                    size="small"
                    onClick={handleStopScheduler}
                    disabled={stopSchedulerMutation.isLoading || systemStatus?.scheduler.status === 'stopped'}
                  >
                    <Stop />
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography variant="body2" color="textSecondary">
                {systemStatus?.scheduler.jobs.length || 0} scheduled jobs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Course Statistics */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <School color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6">Course Statistics</Typography>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {courseStats?.total_courses || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Courses
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {courseStats?.total_sections || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Sections
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {systemStatus?.database.unique_subjects || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Unique Subjects
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {courseStats?.courses_with_sections || 0}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Courses with Sections
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Scheduled Jobs */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Scheduled Jobs
          </Typography>
          {systemStatus?.scheduler.jobs.length === 0 ? (
            <Alert severity="info">No scheduled jobs found.</Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Job Name</TableCell>
                    <TableCell>Next Run</TableCell>
                    <TableCell>Trigger</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {systemStatus?.scheduler.jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.name}</TableCell>
                      <TableCell>{formatNextRun(job.next_run)}</TableCell>
                      <TableCell>
                        <Chip label={job.trigger} size="small" variant="outlined" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Top Subjects */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Top Subjects by Course Count
          </Typography>
          {courseStats?.top_subjects.length === 0 ? (
            <Alert severity="info">No subject data available.</Alert>
          ) : (
            <Grid container spacing={1}>
              {courseStats?.top_subjects.slice(0, 10).map((subject) => (
                <Grid item key={subject.subject}>
                  <Chip
                    label={`${subject.subject} (${subject.count})`}
                    variant="outlined"
                    icon={<TrendingUp />}
                  />
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Admin;
