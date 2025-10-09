import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Grid,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  PlayArrow,
  CheckCircle,
  Edit,
  Delete,
  CalendarToday,
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
  start_date: yup.date().required('Start date is required'),
  end_date: yup.date().required('End date is required'),
});

type FormData = yup.InferType<typeof schema>;

interface StudySession {
  id: number;
  start_time: string;
  end_time: string;
  is_completed: boolean;
  notes?: string;
  assignment_id: number;
  assignment_title?: string;
  course_name?: string;
}

interface ScheduleResponse {
  study_sessions: StudySession[];
  total_hours_scheduled: number;
  assignments_covered: number[];
}

const Schedule: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      start_date: new Date(),
      end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 1 week from now
    },
  });

  const { data: studySessions, isLoading } = useQuery<StudySession[]>(
    'study-sessions',
    async () => {
      const response = await axios.get('/schedules/sessions');
      return response.data;
    }
  );

  const generateScheduleMutation = useMutation(
    async (data: FormData) => {
      const response = await axios.post('/schedules/generate', {
        start_date: data.start_date.toISOString(),
        end_date: data.end_date.toISOString(),
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('study-sessions');
        toast.success('Schedule generated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to generate schedule');
      },
    }
  );

  const completeSessionMutation = useMutation(
    async (id: number) => {
      await axios.patch(`/schedules/sessions/${id}/complete`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('study-sessions');
        toast.success('Study session marked as completed!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to mark session as completed');
      },
    }
  );

  const deleteSessionMutation = useMutation(
    async (id: number) => {
      await axios.delete(`/schedules/sessions/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('study-sessions');
        toast.success('Study session deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete study session');
      },
    }
  );

  const handleOpen = () => {
    reset();
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    reset();
  };

  const onSubmit = async (data: FormData) => {
    setGenerating(true);
    try {
      await generateScheduleMutation.mutateAsync(data);
    } finally {
      setGenerating(false);
    }
  };

  const handleComplete = (id: number) => {
    completeSessionMutation.mutate(id);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this study session?')) {
      deleteSessionMutation.mutate(id);
    }
  };

  const formatDuration = (startTime: string, endTime: string) => {
    const start = dayjs(startTime);
    const end = dayjs(endTime);
    const duration = end.diff(start, 'hour', true);
    return `${duration} hours`;
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Study Schedule</Typography>
        <Button
          variant="contained"
          startIcon={<PlayArrow />}
          onClick={handleOpen}
        >
          Generate Schedule
        </Button>
      </Box>

      {(!studySessions || studySessions.length === 0) && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No study sessions scheduled yet. Generate a schedule to get started!
        </Alert>
      )}

      <Grid container spacing={3}>
        {studySessions?.map((session) => (
          <Grid item xs={12} sm={6} md={4} key={session.id}>
            <Card sx={{ opacity: session.is_completed ? 0.7 : 1 }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <ScheduleIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {session.assignment_title || 'Study Session'}
                  </Typography>
                  {session.is_completed && (
                    <CheckCircle color="success" sx={{ ml: 1 }} />
                  )}
                </Box>
                <Typography color="textSecondary" gutterBottom>
                  {dayjs(session.start_time).format('MMM DD, YYYY')}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {dayjs(session.start_time).format('h:mm A')} - {dayjs(session.end_time).format('h:mm A')}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Duration: {formatDuration(session.start_time, session.end_time)}
                </Typography>
                {session.course_name && (
                  <Typography color="textSecondary" gutterBottom>
                    Course: {session.course_name}
                  </Typography>
                )}
                {session.notes && (
                  <Typography variant="body2" color="textSecondary">
                    {session.notes}
                  </Typography>
                )}
                <Box mt={1}>
                  <Chip
                    label={session.is_completed ? 'Completed' : 'Pending'}
                    color={session.is_completed ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </CardContent>
              <CardActions>
                {!session.is_completed && (
                  <Button
                    size="small"
                    onClick={() => handleComplete(session.id)}
                    startIcon={<CheckCircle />}
                  >
                    Complete
                  </Button>
                )}
                <IconButton
                  size="small"
                  onClick={() => handleDelete(session.id)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Study Schedule</DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Alert severity="info" sx={{ mb: 2 }}>
              This will generate a personalized study schedule based on your assignments and availability.
            </Alert>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <Controller
                name="start_date"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    label="Start Date"
                    value={field.value ? dayjs(field.value) : null}
                    onChange={(date) => field.onChange(date?.toDate())}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'dense',
                        error: !!errors.start_date,
                        helperText: errors.start_date?.message,
                        sx: { mb: 2 }
                      }
                    }}
                  />
                )}
              />
              <Controller
                name="end_date"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    label="End Date"
                    value={field.value ? dayjs(field.value) : null}
                    onChange={(date) => field.onChange(date?.toDate())}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'dense',
                        error: !!errors.end_date,
                        helperText: errors.end_date?.message,
                      }
                    }}
                  />
                )}
              />
            </LocalizationProvider>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting || generating}
              startIcon={generating ? <CircularProgress size={20} /> : <PlayArrow />}
            >
              {generating ? 'Generating...' : 'Generate Schedule'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default Schedule;
