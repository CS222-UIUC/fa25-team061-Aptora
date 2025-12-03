import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  Typography,
} from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

interface NotificationSettings {
  reminders_enabled: boolean;
  reminder_lead_minutes: number;
}

const leadOptions = [
  { label: '5 minutes before', value: 5 },
  { label: '15 minutes before', value: 15 },
  { label: '30 minutes before', value: 30 },
  { label: '1 hour before', value: 60 },
  { label: '2 hours before', value: 120 },
];

const defaultSettings: NotificationSettings = {
  reminders_enabled: true,
  reminder_lead_minutes: 30,
};

const Notifications: React.FC = () => {
  const queryClient = useQueryClient();
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [errors, setErrors] = useState<{ reminder_lead_minutes?: string }>({});

  const {
    data,
    isLoading,
    isFetching,
    isError,
    error,
  } = useQuery<NotificationSettings, Error>(
    'notification-settings',
    async () => {
      const response = await axios.get('/notifications/settings');
      return response.data;
    },
    {
      onSuccess: (fetchedSettings) => {
        setSettings(fetchedSettings ?? defaultSettings);
      },
      onError: () => {
        setSettings(defaultSettings);
      },
      refetchOnWindowFocus: false,
    }
  );

  const updateSettingsMutation = useMutation(
    async (newSettings: NotificationSettings) => {
      await axios.put('/notifications/settings', newSettings);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('notification-settings');
        toast.success('Notification preferences updated');
      },
      onError: (mutationError: any) => {
        toast.error(mutationError?.response?.data?.detail ?? 'Failed to update preferences');
      },
    }
  );

  useEffect(() => {
    if (data) {
      setSettings(data);
    }
  }, [data]);

  const isSaving = updateSettingsMutation.isLoading;

  const hasUnsavedChanges = useMemo(() => {
    if (!settings || !data) {
      return false;
    }
    return (
      settings.reminders_enabled !== data.reminders_enabled ||
      settings.reminder_lead_minutes !== data.reminder_lead_minutes
    );
  }, [data, settings]);

  const handleToggleReminders = (_: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
    setSettings((prev) => (prev ? { ...prev, reminders_enabled: checked } : prev));
  };

  const handleLeadChange = (event: SelectChangeEvent<string>) => {
    const value = Number(event.target.value);
    if (Number.isNaN(value) || value <= 0) {
      setErrors({ reminder_lead_minutes: 'Lead time must be a positive number' });
    } else {
      setErrors({});
    }
    setSettings((prev) => (prev ? { ...prev, reminder_lead_minutes: value } : prev));
  };

  const handleSave = async () => {
    if (!settings) {
      return;
    }

    if (settings.reminder_lead_minutes <= 0) {
      setErrors({ reminder_lead_minutes: 'Lead time must be greater than 0' });
      return;
    }

    await updateSettingsMutation.mutateAsync(settings);
  };

  if (isLoading && !settings) {
    return <LoadingSpinner message="Loading notification settings..." />;
  }

  if (isError && !settings) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          {error?.message ?? 'Unable to fetch notification settings.'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box display="flex" flexDirection="column" gap={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Notifications
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage reminders for upcoming study sessions. These settings control how and when Aptora
            notifies you about scheduled sessions.
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" flexDirection="column" gap={2}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings?.reminders_enabled ?? defaultSettings.reminders_enabled}
                        onChange={handleToggleReminders}
                        color="primary"
                        disabled={isSaving}
                      />
                    }
                    label="Enable reminders for upcoming study sessions"
                  />
                  <Typography variant="body2" color="textSecondary">
                    When enabled, Aptora will send you an email reminder before each study session.
                  </Typography>

                  <FormControl
                    fullWidth
                    disabled={!(settings?.reminders_enabled ?? defaultSettings.reminders_enabled) || isSaving}
                    error={Boolean(errors.reminder_lead_minutes)}
                  >
                    <InputLabel id="reminder-lead-label">
                      Reminder lead time
                    </InputLabel>
                    <Select
                      labelId="reminder-lead-label"
                      value={String(settings?.reminder_lead_minutes ?? defaultSettings.reminder_lead_minutes)}
                      label="Reminder lead time"
                      onChange={handleLeadChange}
                    >
                      {leadOptions.map((option) => (
                        <MenuItem key={option.value} value={String(option.value)}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>
                      {errors.reminder_lead_minutes ??
                        'Choose how long before a session you want to be notified.'}
                    </FormHelperText>
                  </FormControl>

                  {(isFetching || isSaving) && (
                    <Typography variant="body2" color="textSecondary">
                      {isSaving ? 'Saving your changes…' : 'Refreshing settings…'}
                    </Typography>
                  )}

                  <Box display="flex" gap={2}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleSave}
                      disabled={isSaving || !settings || !hasUnsavedChanges}
                    >
                      {isSaving ? 'Saving...' : 'Save changes'}
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => setSettings(data ?? defaultSettings)}
                      disabled={isSaving || !hasUnsavedChanges}
                    >
                      Reset
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Notifications;

