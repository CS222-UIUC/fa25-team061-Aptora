import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 4,
      }}
    >
      <Container maxWidth="md">
        <Box
          sx={{
            textAlign: 'center',
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: 4,
            padding: 6,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}
        >
          {/* Back Button */}
          <Box sx={{ textAlign: 'left', mb: 4 }}>
            <Button
              component={Link}
              to="/"
              startIcon={<ArrowBack />}
              sx={{
                color: 'white',
                borderColor: 'white',
                '&:hover': {
                  borderColor: 'white',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
              variant="outlined"
            >
              Back to Home
            </Button>
          </Box>

          {/* About Title */}
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 'bold',
              mb: 4,
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)',
            }}
          >
            About Us
          </Typography>

          {/* About Content */}
          <Typography
            variant="h6"
            sx={{
              lineHeight: 1.8,
              mb: 3,
              textAlign: 'left',
              maxWidth: '800px',
              mx: 'auto',
              textShadow: '1px 1px 2px rgba(0, 0, 0, 0.2)',
            }}
          >
            We built Smart Study Scheduler because we know how overwhelming college life can get. 
            Between classes, deadlines, and exams, staying organized isn't easy—and traditional 
            planners don't always adapt to how you actually work.
          </Typography>

          <Typography
            variant="h6"
            sx={{
              lineHeight: 1.8,
              textAlign: 'left',
              maxWidth: '800px',
              mx: 'auto',
              textShadow: '1px 1px 2px rgba(0, 0, 0, 0.2)',
            }}
          >
            Our app helps students create study plans that fit their unique schedules and habits. 
            By learning from your input and productivity trends, it helps you manage your time 
            efficiently, reduce stress, and stay on track.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default About;
