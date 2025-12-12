import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Avatar,
  Paper,
  Divider,
} from '@mui/material';
import {
  School,
  Schedule,
  AutoAwesome,
  People,
  TrendingUp,
  Security,
} from '@mui/icons-material';

const About: React.FC = () => {
  const features = [
    {
      icon: <Schedule fontSize="large" />,
      title: 'Smart Scheduling',
      description: 'AI-powered schedule generation that optimizes your study time based on your assignments, availability, and preferences.',
    },
    {
      icon: <AutoAwesome fontSize="large" />,
      title: 'ML-Powered Insights',
      description: 'Get intelligent predictions about study time requirements and course difficulty using machine learning algorithms.',
    },
    {
      icon: <School fontSize="large" />,
      title: 'Course Management',
      description: 'Easily add and manage your courses, track assignments, and stay organized throughout the semester.',
    },
    {
      icon: <TrendingUp fontSize="large" />,
      title: 'Progress Tracking',
      description: 'Monitor your academic progress, track completed assignments, and visualize your study patterns.',
    },
    {
      icon: <Security fontSize="large" />,
      title: 'Secure & Private',
      description: 'Your data is encrypted and secure. We prioritize your privacy and academic information.',
    },
    {
      icon: <People fontSize="large" />,
      title: 'Personalized Experience',
      description: 'Customize your study schedule based on your learning style, availability, and academic goals.',
    },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        paddingTop: '80px',
        paddingBottom: '60px',
      }}
    >
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box
          sx={{
            textAlign: 'center',
            color: 'white',
            mb: 8,
            pt: 4,
          }}
        >
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 'bold',
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
              mb: 2,
            }}
          >
            About Aptora
          </Typography>
          <Typography
            variant="h5"
            component="p"
            sx={{
              maxWidth: '800px',
              margin: '0 auto',
              opacity: 0.95,
              textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
            }}
          >
            Your intelligent study companion designed to help students optimize their time,
            manage coursework, and achieve academic success through AI-powered scheduling.
          </Typography>
        </Box>

        {/* Mission Section */}
        <Paper
          elevation={8}
          sx={{
            p: 4,
            mb: 6,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.98)',
          }}
        >
          <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
            Our Mission
          </Typography>
          <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
            Aptora was created to solve a common problem faced by students: how to effectively
            manage time and balance multiple courses, assignments, and personal commitments.
            We believe that with the right tools and intelligent planning, every student can
            achieve their academic goals while maintaining a healthy work-life balance.
          </Typography>
          <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
            Our platform combines machine learning algorithms, user preferences, and course data
            to generate personalized study schedules that adapt to your unique learning style
            and availability.
          </Typography>
        </Paper>

        {/* Features Section */}
        <Box sx={{ mb: 6 }}>
          <Typography
            variant="h4"
            component="h2"
            gutterBottom
            sx={{
              textAlign: 'center',
              color: 'white',
              fontWeight: 'bold',
              mb: 4,
              textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
            }}
          >
            Key Features
          </Typography>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'transform 0.3s, box-shadow 0.3s',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        width: 64,
                        height: 64,
                        margin: '0 auto 16px',
                        color: 'white',
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h6" component="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Technology Section */}
        <Paper
          elevation={8}
          sx={{
            p: 4,
            mb: 6,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.98)',
          }}
        >
          <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
            Technology & Innovation
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Machine Learning
              </Typography>
              <Typography variant="body1" paragraph>
                Our ML models analyze course difficulty, assignment patterns, and historical data
                to predict study time requirements and optimize your schedule.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Intelligent Scheduling
              </Typography>
              <Typography variant="body1" paragraph>
                Advanced algorithms consider your availability, assignment deadlines, course priorities,
                and personal preferences to create the most efficient study schedule.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Data Integration
              </Typography>
              <Typography variant="body1" paragraph>
                We integrate with course catalogs and utilize web scraping to provide comprehensive
                course information and professor ratings to help you make informed decisions.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Real-time Updates
              </Typography>
              <Typography variant="body1" paragraph>
                Your schedule adapts in real-time as you add assignments, update availability,
                or mark tasks as complete, ensuring you're always on track.
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Team Section */}
        <Paper
          elevation={8}
          sx={{
            p: 4,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.98)',
            textAlign: 'center',
          }}
        >
          <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
            Built for Students, by Students
          </Typography>
          <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.8, maxWidth: '800px', margin: '0 auto' }}>
            Aptora is developed by a team of students who understand the challenges of academic life.
            We're committed to continuously improving the platform based on user feedback and
            the evolving needs of the student community.
          </Typography>
          <Divider sx={{ my: 4 }} />
          <Typography variant="body2" color="text.secondary">
            © 2025 Aptora. All rights reserved.
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default About;
