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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  AccessTime,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

const schema = yup.object({
  day_of_week: yup.number().min(0).max(6).required('Day of week is required'),
  start_time: yup.string().required('Start time is required'),
  end_time: yup.string().required('End time is required'),
});

type FormData = yup.InferType<typeof schema>;

interface AvailabilitySlot {
  id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  created_at: string;
}

const dayNames = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];

const Availability: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [editingSlot, setEditingSlot] = useState<AvailabilitySlot | null>(null);
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

  const { data: availabilitySlots, isLoading } = useQuery<AvailabilitySlot[]>(
    'availability-slots',
    async () => {
      const response = await axios.get('/availability/');
      return response.data;
    }
  );

  const createMutation = useMutation(
    async (data: FormData) => {
      const response = await axios.post('/availability/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('availability-slots');
        toast.success('Availability slot created successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create availability slot');
      },
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: FormData }) => {
      const response = await axios.put(`/availability/${id}`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('availability-slots');
        toast.success('Availability slot updated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update availability slot');
      },
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      await axios.delete(`/availability/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('availability-slots');
        toast.success('Availability slot deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete availability slot');
      },
    }
  );

  const handleOpen = () => {
    setEditingSlot(null);
    reset();
    setOpen(true);
  };

  const handleEdit = (slot: AvailabilitySlot) => {
    setEditingSlot(slot);
    reset({
      day_of_week: slot.day_of_week,
      start_time: slot.start_time,
      end_time: slot.end_time,
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingSlot(null);
    reset();
  };

  const onSubmit = async (data: FormData) => {
    if (editingSlot) {
      updateMutation.mutate({ id: editingSlot.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this availability slot?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Availability</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpen}
        >
          Add Availability Slot
        </Button>
      </Box>

      <Grid container spacing={3}>
        {availabilitySlots?.map((slot) => (
          <Grid item xs={12} sm={6} md={4} key={slot.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AccessTime color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {dayNames[slot.day_of_week]}
                  </Typography>
                </Box>
                <Typography color="textSecondary" gutterBottom>
                  {slot.start_time} - {slot.end_time}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Duration: {(() => {
                    const start = dayjs(slot.start_time, 'HH:mm');
                    const end = dayjs(slot.end_time, 'HH:mm');
                    const duration = end.diff(start, 'hour', true);
                    return `${duration} hours`;
                  })()}
                </Typography>
              </CardContent>
              <CardActions>
                <IconButton
                  size="small"
                  onClick={() => handleEdit(slot)}
                >
                  <Edit />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDelete(slot.id)}
                  color="error"
                >
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {(!availabilitySlots || availabilitySlots.length === 0) && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="textSecondary">
            No availability slots set. Add your available study times!
          </Typography>
        </Box>
      )}

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSlot ? 'Edit Availability Slot' : 'Add New Availability Slot'}
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
              <InputLabel>Day of Week</InputLabel>
              <Select
                {...register('day_of_week', { valueAsNumber: true })}
                error={!!errors.day_of_week}
              >
                {dayNames.map((day, index) => (
                  <MenuItem key={index} value={index}>
                    {day}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <Controller
                name="start_time"
                control={control}
                render={({ field }) => (
                  <TimePicker
                    label="Start Time"
                    value={field.value ? dayjs(field.value, 'HH:mm') : null}
                    onChange={(time) => field.onChange(time?.format('HH:mm'))}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'dense',
                        error: !!errors.start_time,
                        helperText: errors.start_time?.message,
                        sx: { mb: 2 }
                      }
                    }}
                  />
                )}
              />
              <Controller
                name="end_time"
                control={control}
                render={({ field }) => (
                  <TimePicker
                    label="End Time"
                    value={field.value ? dayjs(field.value, 'HH:mm') : null}
                    onChange={(time) => field.onChange(time?.format('HH:mm'))}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'dense',
                        error: !!errors.end_time,
                        helperText: errors.end_time?.message,
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
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : editingSlot ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default Availability;
