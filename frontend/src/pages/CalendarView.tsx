import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import Calendar from '../components/Calendar';

const CalendarView: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          Calendar View
        </Typography>
        <Typography variant="body1" color="textSecondary">
          View your study schedule and assignment due dates in a calendar format.
        </Typography>
      </Box>
      <Calendar />
    </Container>
  );
};

export default CalendarView;
