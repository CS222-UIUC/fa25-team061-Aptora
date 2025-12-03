import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Dashboard from '../pages/Dashboard';
import Courses from '../pages/Courses';
import Assignments from '../pages/Assignments';
import Availability from '../pages/Availability';
import Schedule from '../pages/Schedule';
import CalendarView from '../pages/CalendarView';
import Notifications from '../pages/Notifications';
import Login from '../pages/Login';
import Register from '../pages/Register';
import About from '../pages/About';
import Admin from '../pages/Admin';

const AppRouter: React.FC = () => {
  const location = useLocation();
  const isAboutPage = location.pathname === '/app/about';
  
  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div style={{ paddingTop: isAboutPage ? '0' : '80px' }}>
        <Routes>
          <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses" element={<Courses />} />
          <Route path="/assignments" element={<Assignments />} />
          <Route path="/availability" element={<Availability />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/calendar" element={<CalendarView />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/about" element={<About />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </div>
    </div>
  );
};

export default AppRouter;
