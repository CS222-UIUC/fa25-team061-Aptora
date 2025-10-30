import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Dashboard,
  School,
  Assignment,
  Schedule,
  AccessTime,
  CalendarToday,
  Home,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/app/login');
    handleClose();
  };

  const navigationItems = [
    { path: '/app/dashboard', label: 'Dashboard', icon: <Dashboard /> },
    { path: '/app/courses', label: 'Courses', icon: <School /> },
    { path: '/app/assignments', label: 'Assignments', icon: <Assignment /> },
    { path: '/app/schedule', label: 'Schedule', icon: <Schedule /> },
    { path: '/app/calendar', label: 'Calendar', icon: <CalendarToday /> },
    { path: '/app/availability', label: 'Availability', icon: <AccessTime /> },
    { path: '/app/admin', label: 'Admin', icon: <Settings /> },
  ];

  const isAboutPage = location.pathname === '/app/about';

  return (
    <AppBar 
      position="static"
      sx={{
        backgroundColor: isAboutPage ? 'transparent' : 'primary.main',
        background: isAboutPage ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'primary.main',
        boxShadow: isAboutPage ? 'none' : 1,
      }}
    >
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            cursor: 'pointer',
            color: isAboutPage ? 'white' : 'inherit',
            textShadow: isAboutPage ? '2px 2px 4px rgba(0,0,0,0.5)' : 'none',
            '&:hover': {
              opacity: 0.8
            }
          }}
          onClick={() => navigate('/')}
        >
          Aptora
        </Typography>
        
        {!isAboutPage && (
          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            Home
          </Button>
        )}
        
        {user && !isAboutPage && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {navigationItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                startIcon={item.icon}
                onClick={() => navigate(item.path)}
                sx={{
                  backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                }}
              >
                {item.label}
              </Button>
            ))}
            
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem disabled>
                {user.first_name} {user.last_name}
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        )}

        {!user && !isAboutPage && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Button color="inherit" onClick={() => navigate('/app/login')}>
              Login
            </Button>
            <Button color="inherit" onClick={() => navigate('/app/register')}>
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
