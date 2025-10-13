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
  Chip,
} from '@mui/material';
import {
  School,
  TrendingUp,
  Notifications,
  CalendarToday,
  Analytics,
  ArrowForward,
  Menu,
  Close,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import LandingCourseSearch from '../components/LandingCourseSearch';
import { CourseCatalog } from '../services/courseCatalogService';

const LandingPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const features = [
    {
      icon: <School sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      title: 'Course Catalog Integration',
      description: 'Access the complete UIUC course catalog with 4,500+ courses. Search, browse, and select your courses instantly.',
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
            Aptora
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
              <Button color="inherit" component={Link} to="/app/about">
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
              Aptora
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
            
            {/* Course Search Section */}
            <Box sx={{ mb: 6 }}>
              <LandingCourseSearch
                onCourseSelect={(course: CourseCatalog) => {
                  console.log('Selected course:', course);
                  // You can add logic here to store the selected course
                }}
                onGetStarted={() => {
                  // Navigate to the app with the selected course
                  window.location.href = '/app/courses';
                }}
              />
            </Box>
            
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
              Why Choose Aptora?
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

        {/* Course Catalog Showcase */}
        <Fade in timeout={1500}>
          <Box sx={{ mb: 8 }}>
            <Typography
              variant="h3"
              sx={{
                color: 'white',
                textAlign: 'center',
                mb: 6,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              }}
            >
              Discover Your Courses
            </Typography>
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box sx={{ pr: { xs: 0, md: 4 } }}>
                  <Typography
                    variant="h5"
                    sx={{
                      color: 'white',
                      mb: 3,
                      textShadow: '0 1px 2px rgba(0,0,0,0.3)',
                    }}
                  >
                    Complete UIUC Course Catalog
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.9)',
                      mb: 3,
                      lineHeight: 1.8,
                    }}
                  >
                    Access over 4,500 courses from all departments at the University of Illinois. 
                    Search by subject, course number, or keywords to find exactly what you need.
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                    {['CS', 'MATH', 'PHYS', 'CHEM', 'ECON', 'ENG'].map((subject) => (
                      <Chip
                        key={subject}
                        label={subject}
                        sx={{
                          backgroundColor: 'rgba(255, 255, 255, 0.2)',
                          color: 'white',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                        }}
                      />
                    ))}
                    <Chip
                      label="+180 more"
                      sx={{
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'rgba(255, 255, 255, 0.8)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                      }}
                    />
                  </Box>
                  <Button
                    variant="contained"
                    size="large"
                    component={Link}
                    to="/app/courses"
                    endIcon={<ArrowForward />}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #764ba2 30%, #667eea 90%)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    Browse All Courses
                  </Button>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card
                  sx={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 3,
                    p: 3,
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  <Typography variant="h6" sx={{ mb: 2, color: 'text.primary' }}>
                    Popular Courses
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {[
                      { code: 'CS 225', title: 'Data Structures', credits: 4 },
                      { code: 'MATH 241', title: 'Calculus III', credits: 4 },
                      { code: 'PHYS 211', title: 'University Physics: Mechanics', credits: 4 },
                      { code: 'ECON 302', title: 'Intermediate Microeconomic Theory', credits: 3 },
                    ].map((course, index) => (
                      <Box
                        key={course.code}
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 2,
                          backgroundColor: 'background.paper',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: 'action.hover',
                            transform: 'translateX(4px)',
                          },
                        }}
                      >
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {course.code}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {course.title}
                          </Typography>
                        </Box>
                        <Chip
                          label={`${course.credits} credits`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    ))}
                  </Box>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </Fade>

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
              Join thousands of students who have improved their academic performance with Aptora's smart scheduling system. 
              Start by selecting your courses and let AI create your perfect study schedule.
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
          © 2025 Aptora. Built with ❤️ for students everywhere.
        </Typography>
      </Box>
    </Box>
  );
};

export default LandingPage;