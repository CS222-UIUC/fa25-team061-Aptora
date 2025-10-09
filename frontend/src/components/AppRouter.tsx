import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './Navbar';
import Dashboard from '../pages/Dashboard';
import Courses from '../pages/Courses';
import Assignments from '../pages/Assignments';
import Availability from '../pages/Availability';
import Schedule from '../pages/Schedule';
import CalendarView from '../pages/CalendarView';
import Login from '../pages/Login';
import Register from '../pages/Register';

const AppRouter: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, pt: 8 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/assignments" element={<Assignments />} />
          <Route path="/availability" element={<Availability />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/calendar" element={<CalendarView />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Box>
    </Box>
  );
};

export default AppRouter;
