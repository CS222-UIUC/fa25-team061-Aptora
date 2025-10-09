import React, { useState } from 'react';
import { Calendar as BigCalendar, momentLocalizer, Views } from 'react-big-calendar';
import moment from 'moment';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  CheckCircle,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

interface CalendarEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: {
    type: 'study_session' | 'assignment_due';
    assignment_id?: number;
    session_id?: number;
    is_completed?: boolean;
    course_name?: string;
    difficulty?: string;
  };
}

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

interface Assignment {
  id: number;
  title: string;
  due_date: string;
  difficulty: string;
  course_name?: string;
}

const Calendar: React.FC = () => {
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [open, setOpen] = useState(false);
  const [editingSession, setEditingSession] = useState<StudySession | null>(null);
  const queryClient = useQueryClient();

  const { data: studySessions, isLoading: sessionsLoading } = useQuery<StudySession[]>(
    'study-sessions',
    async () => {
      const response = await axios.get('/schedules/sessions');
      return response.data;
    }
  );

  const { data: assignments, isLoading: assignmentsLoading } = useQuery<Assignment[]>(
    'assignments',
    async () => {
      const response = await axios.get('/assignments/');
      return response.data;
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
        setOpen(false);
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
        setOpen(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete study session');
      },
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

  const getEventStyle = (event: CalendarEvent) => {
    if (event.resource.type === 'study_session') {
      return {
        style: {
          backgroundColor: event.resource.is_completed ? '#4caf50' : '#2196f3',
          borderRadius: '4px',
          border: 'none',
          color: 'white',
          padding: '2px 4px',
        }
      };
    } else {
      return {
        style: {
          backgroundColor: '#ff9800',
          borderRadius: '4px',
          border: 'none',
          color: 'white',
          padding: '2px 4px',
        }
      };
    }
  };

  const formatEvents = (): CalendarEvent[] => {
    const events: CalendarEvent[] = [];

    // Add study sessions
    studySessions?.forEach((session) => {
      events.push({
        id: session.id,
        title: session.assignment_title || 'Study Session',
        start: new Date(session.start_time),
        end: new Date(session.end_time),
        resource: {
          type: 'study_session',
          session_id: session.id,
          assignment_id: session.assignment_id,
          is_completed: session.is_completed,
          course_name: session.course_name,
        },
      });
    });

    // Add assignment due dates
    assignments?.forEach((assignment) => {
      if (!assignment.due_date) return;
      
      const dueDate = new Date(assignment.due_date);
      events.push({
        id: assignment.id + 10000, // Offset to avoid ID conflicts
        title: `Due: ${assignment.title}`,
        start: dueDate,
        end: new Date(dueDate.getTime() + 60 * 60 * 1000), // 1 hour duration
        resource: {
          type: 'assignment_due',
          assignment_id: assignment.id,
          course_name: assignment.course_name,
          difficulty: assignment.difficulty,
        },
      });
    });

    return events;
  };

  const handleSelectEvent = (event: CalendarEvent) => {
    setSelectedEvent(event);
    if (event.resource.type === 'study_session') {
      const session = studySessions?.find(s => s.id === event.resource.session_id);
      setEditingSession(session || null);
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedEvent(null);
    setEditingSession(null);
  };

  const handleComplete = () => {
    if (editingSession) {
      completeSessionMutation.mutate(editingSession.id);
    }
  };

  const handleDelete = () => {
    if (editingSession) {
      if (window.confirm('Are you sure you want to delete this study session?')) {
        deleteSessionMutation.mutate(editingSession.id);
      }
    }
  };

  if (sessionsLoading || assignmentsLoading) {
    return <div>Loading calendar...</div>;
  }

  const events = formatEvents();

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          Study Schedule Calendar
        </Typography>
        <Box display="flex" gap={1} mb={2}>
          <Chip label="Study Sessions" color="primary" size="small" />
          <Chip label="Assignment Due Dates" color="warning" size="small" />
        </Box>
      </Paper>

      <Paper sx={{ height: '600px' }}>
        <BigCalendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          views={[Views.MONTH, Views.WEEK, Views.DAY]}
          defaultView={Views.WEEK}
          onSelectEvent={handleSelectEvent}
          eventPropGetter={getEventStyle}
          popup
        />
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedEvent?.resource.type === 'study_session' ? 'Study Session Details' : 'Assignment Due Date'}
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedEvent.title}
              </Typography>
              <Typography color="textSecondary" gutterBottom>
                {moment(selectedEvent.start).format('MMMM DD, YYYY')}
              </Typography>
              <Typography color="textSecondary" gutterBottom>
                {moment(selectedEvent.start).format('h:mm A')} - {moment(selectedEvent.end).format('h:mm A')}
              </Typography>
              
              {selectedEvent.resource.course_name && (
                <Typography color="textSecondary" gutterBottom>
                  Course: {selectedEvent.resource.course_name}
                </Typography>
              )}

              {selectedEvent.resource.difficulty && (
                <Box mb={2}>
                  <Chip
                    label={selectedEvent.resource.difficulty}
                    color={getDifficultyColor(selectedEvent.resource.difficulty) as any}
                    size="small"
                  />
                </Box>
              )}

              {editingSession?.notes && (
                <Typography variant="body2" color="textSecondary">
                  Notes: {editingSession.notes}
                </Typography>
              )}

              {selectedEvent.resource.type === 'study_session' && (
                <Box mt={2}>
                  <Chip
                    label={selectedEvent.resource.is_completed ? 'Completed' : 'Pending'}
                    color={selectedEvent.resource.is_completed ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedEvent?.resource.type === 'study_session' && !selectedEvent.resource.is_completed && (
            <Button
              onClick={handleComplete}
              startIcon={<CheckCircle />}
              color="success"
            >
              Mark Complete
            </Button>
          )}
          {selectedEvent?.resource.type === 'study_session' && (
            <Button
              onClick={handleDelete}
              startIcon={<Delete />}
              color="error"
            >
              Delete
            </Button>
          )}
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Calendar;
