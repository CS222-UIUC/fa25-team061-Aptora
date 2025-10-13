import React, { useState } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Grid,
} from '@mui/material';
import {
  Search,
  School,
  Schedule,
  Person,
  ArrowForward,
} from '@mui/icons-material';
import { useCourseCatalog } from '../hooks/useCourseCatalog';
import { CourseCatalog } from '../services/courseCatalogService';

interface LandingCourseSearchProps {
  onCourseSelect?: (course: CourseCatalog) => void;
  onGetStarted?: () => void;
}

const LandingCourseSearch: React.FC<LandingCourseSearchProps> = ({
  onCourseSelect,
  onGetStarted,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCourse, setSelectedCourse] = useState<CourseCatalog | null>(null);
  
  const {
    courses,
    loadingCourses,
    error,
    searchCourses,
    clearError,
  } = useCourseCatalog({ autoLoad: false });

  // Debounced search
  React.useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        searchCourses(searchQuery);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchCourses]);

  const handleCourseSelect = (course: CourseCatalog) => {
    setSelectedCourse(course);
    onCourseSelect?.(course);
  };

  const handleGetStarted = () => {
    onGetStarted?.();
  };

  const formatCourseOption = (course: CourseCatalog) => (
    <Box sx={{ width: '100%', py: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'white' }}>
          {course.subject} {course.number}
        </Typography>
        {course.credit_hours && (
          <Chip 
            label={`${course.credit_hours} credits`} 
            size="small" 
            sx={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)'
            }}
          />
        )}
      </Box>
      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
        {course.title}
      </Typography>
    </Box>
  );

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto' }}>
      <Typography 
        variant="h5" 
        sx={{ 
          color: 'white', 
          mb: 3, 
          textAlign: 'center',
          textShadow: '0 1px 2px rgba(0,0,0,0.3)'
        }}
      >
        Find Your Courses
      </Typography>
      
      <Autocomplete
        options={courses}
        loading={loadingCourses}
        value={selectedCourse}
        onChange={(_, newValue) => newValue && handleCourseSelect(newValue)}
        onInputChange={(_, newValue) => setSearchQuery(newValue)}
        getOptionLabel={(course) => `${course.subject} ${course.number}: ${course.title}`}
        renderOption={(props, course) => (
          <li {...props} style={{ backgroundColor: 'rgba(102, 126, 234, 0.9)' }}>
            {formatCourseOption(course)}
          </li>
        )}
        renderInput={(params) => (
          <TextField
            {...params}
            placeholder="Search for your courses (e.g., CS 225, MATH 241)"
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderRadius: 3,
                '& fieldset': {
                  border: 'none',
                },
                '&:hover fieldset': {
                  border: 'none',
                },
                '&.Mui-focused fieldset': {
                  border: '2px solid rgba(255, 255, 255, 0.8)',
                },
              },
              '& .MuiInputBase-input': {
                fontSize: '1.1rem',
                padding: '16px 20px',
              },
            }}
            InputProps={{
              ...params.InputProps,
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              endAdornment: (
                <>
                  {loadingCourses && <CircularProgress color="inherit" size={20} />}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        noOptionsText={
          searchQuery.trim() ? 
            (loadingCourses ? 'Searching...' : 'No courses found') : 
            'Start typing to search for courses'
        }
        filterOptions={(options) => options}
        isOptionEqualToValue={(option, value) => 
          option.subject === value.subject && option.number === value.number
        }
        sx={{ mb: 3 }}
      />

      {error && (
        <Alert 
          severity="error" 
          onClose={clearError}
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
      )}

      {selectedCourse && (
        <Card sx={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: 3,
          mb: 3,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <School color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {selectedCourse.subject} {selectedCourse.number}
              </Typography>
              {selectedCourse.credit_hours && (
                <Chip 
                  label={`${selectedCourse.credit_hours} credits`} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
            
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
              {selectedCourse.title}
            </Typography>
            
            {selectedCourse.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedCourse.description.substring(0, 200)}...
              </Typography>
            )}

            {selectedCourse.sections.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Available Sections:
                </Typography>
                <Grid container spacing={1}>
                  {selectedCourse.sections.slice(0, 3).map((section) => (
                    <Grid item xs={12} sm={4} key={section.id}>
                      <Box sx={{ 
                        p: 1, 
                        border: '1px solid', 
                        borderColor: 'divider', 
                        borderRadius: 1,
                        backgroundColor: 'background.paper'
                      }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                          <Schedule sx={{ fontSize: 12 }} />
                          <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                            {section.days || 'TBA'}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {section.times || 'Time TBA'}
                        </Typography>
                        {section.instructor && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                            <Person sx={{ fontSize: 12 }} />
                            <Typography variant="caption" color="text.secondary">
                              {section.instructor}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Grid>
                  ))}
                  {selectedCourse.sections.length > 3 && (
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">
                        +{selectedCourse.sections.length - 3} more sections
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}

            <Button
              variant="contained"
              size="large"
              endIcon={<ArrowForward />}
              onClick={handleGetStarted}
              sx={{
                width: '100%',
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
              Add This Course & Get Started
            </Button>
          </CardContent>
        </Card>
      )}

      {courses.length > 0 && searchQuery.trim() && !selectedCourse && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ color: 'white', mb: 2, textAlign: 'center' }}>
            Search Results ({courses.length})
          </Typography>
          
          <Grid container spacing={2}>
            {courses.slice(0, 6).map((course) => (
              <Grid item xs={12} sm={6} md={4} key={`${course.subject}-${course.number}`}>
                <Card 
                  sx={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                    }
                  }}
                  onClick={() => handleCourseSelect(course)}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {course.subject} {course.number}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {course.title}
                    </Typography>
                    {course.credit_hours && (
                      <Chip 
                        label={`${course.credit_hours} credits`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {courses.length > 6 && (
            <Typography variant="caption" color="rgba(255, 255, 255, 0.8)" sx={{ textAlign: 'center', display: 'block', mt: 2 }}>
              Showing first 6 results. Select a course to get started!
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default LandingCourseSearch;
