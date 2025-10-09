import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  useTheme,
  useMediaQuery,
  Fade,
  Slide,
  IconButton,
} from '@mui/material';
import {
  School,
  Schedule,
  TrendingUp,
  Notifications,
  CalendarToday,
  Analytics,
  ArrowForward,
  Menu,
  Close,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const features = [
    {
      icon: <Schedule sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      title: 'Smart Scheduling',
      description: 'AI-powered study schedule generation based on your availability, course load, and learning preferences.',
    },
    {
      icon: <CalendarToday sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      title: 'Calendar Integration',
      description: 'Seamlessly sync with your existing calendar and get reminders for upcoming study sessions.',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      title: 'Progress Tracking',
      description: 'Monitor your study progress with detailed analytics and performance insights.',
    },
    {
      icon: <Notifications sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      title: 'Smart Notifications',
      description: 'Get timely reminders and study suggestions to stay on track with your goals.',
    },
    {
      icon: <Analytics sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      title: 'Performance Analytics',
      description: 'Track your study patterns and optimize your learning strategy with data-driven insights.',
    },
    {
      icon: <School sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      title: 'Course Management',
      description: 'Organize your courses, assignments, and deadlines in one centralized platform.',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Navigation */}
      <AppBar position="static" sx={{ background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Smart Study Scheduler
          </Typography>
          {isMobile ? (
            <IconButton
              color="inherit"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <Close /> : <Menu />}
            </IconButton>
          ) : (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button color="inherit" component={Link} to="/app">
                Dashboard
              </Button>
              <Button color="inherit" component={Link} to="/app">
                Features
              </Button>
              <Button color="inherit" component={Link} to="/app">
                About
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Fade in timeout={1000}>
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography
              variant="h1"
              sx={{
                color: 'white',
                mb: 3,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                background: 'linear-gradient(45deg, #fff 30%, #f0f0f0 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Smart Study Scheduler
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                mb: 4,
                maxWidth: '600px',
                mx: 'auto',
                textShadow: '0 1px 2px rgba(0,0,0,0.3)',
              }}
            >
              Transform your study habits with AI-powered scheduling, progress tracking, and personalized learning insights.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                component={Link}
                to="/app"
                endIcon={<ArrowForward />}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 3,
                  background: 'linear-gradient(45deg, #ff6b6b 30%, #ee5a24 90%)',
                  boxShadow: '0 4px 15px rgba(255, 107, 107, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #ee5a24 30%, #ff6b6b 90%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 20px rgba(255, 107, 107, 0.6)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                Get Started
              </Button>
              <Button
                variant="outlined"
                size="large"
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 3,
                  borderColor: 'white',
                  color: 'white',
                  '&:hover': {
                    borderColor: 'white',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                Learn More
              </Button>
            </Box>
          </Box>
        </Fade>

        {/* Features Section */}
        <Slide direction="up" in timeout={1500}>
          <Box sx={{ mb: 8 }}>
            <Typography
              variant="h2"
              sx={{
                color: 'white',
                textAlign: 'center',
                mb: 6,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              }}
            >
              Why Choose Smart Study Scheduler?
            </Typography>
            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Fade in timeout={1000 + index * 200}>
                    <Card
                      sx={{
                        height: '100%',
                        background: 'rgba(255, 255, 255, 0.1)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: 3,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          transform: 'translateY(-8px)',
                          boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
                          background: 'rgba(255, 255, 255, 0.15)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: 3, textAlign: 'center' }}>
                        <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                        <Typography
                          variant="h6"
                          sx={{
                            color: 'white',
                            mb: 2,
                            fontWeight: 600,
                          }}
                        >
                          {feature.title}
                        </Typography>
                        <Typography
                          sx={{
                            color: 'rgba(255, 255, 255, 0.8)',
                            lineHeight: 1.6,
                          }}
                        >
                          {feature.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Fade>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Slide>

        {/* CTA Section */}
        <Fade in timeout={2000}>
          <Box
            sx={{
              textAlign: 'center',
              p: 6,
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <Typography
              variant="h3"
              sx={{
                color: 'white',
                mb: 3,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              }}
            >
              Ready to Transform Your Study Habits?
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                mb: 4,
                maxWidth: '500px',
                mx: 'auto',
              }}
            >
              Join thousands of students who have improved their academic performance with our smart scheduling system.
            </Typography>
            <Button
              variant="contained"
              size="large"
              component={Link}
              to="/app"
              endIcon={<ArrowForward />}
              sx={{
                px: 6,
                py: 2,
                borderRadius: 3,
                background: 'linear-gradient(45deg, #4facfe 30%, #00f2fe 90%)',
                boxShadow: '0 4px 15px rgba(79, 172, 254, 0.4)',
                fontSize: '1.1rem',
                '&:hover': {
                  background: 'linear-gradient(45deg, #00f2fe 30%, #4facfe 90%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(79, 172, 254, 0.6)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              Start Your Journey
            </Button>
          </Box>
        </Fade>
      </Container>

      {/* Footer */}
      <Box
        sx={{
          py: 4,
          textAlign: 'center',
          background: 'rgba(0, 0, 0, 0.2)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          © 2024 Smart Study Scheduler. Built with ❤️ for students everywhere.
        </Typography>
      </Box>
    </Box>
  );
};

export default LandingPage;
