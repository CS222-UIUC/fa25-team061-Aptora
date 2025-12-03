import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Chip,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  Add,
  Info,
  Schedule,
  Person,
} from '@mui/icons-material';
import { useCourseCatalog } from '../hooks/useCourseCatalog';
import { CourseCatalog } from '../services/courseCatalogService';

interface CourseSearchProps {
  onCourseSelect?: (course: CourseCatalog) => void;
  onCourseAdd?: (course: CourseCatalog) => void;
  selectedCourses?: CourseCatalog[];
  showAddButton?: boolean;
  placeholder?: string;
  maxResults?: number;
}

const CourseSearch: React.FC<CourseSearchProps> = ({
  onCourseSelect,
  onCourseAdd,
  selectedCourses = [],
  showAddButton = true,
  placeholder = "Search for courses (e.g., CS 225, MATH 241)",
  maxResults = 50,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  
  const {
    courses,
    loadingCourses,
    error,
    searchCourses,
    clearError,
  } = useCourseCatalog({ autoLoad: false });

  // Debounced search - clear immediately if empty, otherwise debounce
  useEffect(() => {
    // If search is empty, clear immediately
    if (!searchQuery.trim()) {
      searchCourses(''); // This will clear courses in the hook
      return;
    }

    // Otherwise, debounce the search
    const timeoutId = setTimeout(() => {
      searchCourses(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchCourses]);

  const handleCourseSelect = (course: CourseCatalog) => {
    onCourseSelect?.(course);
    setIsOpen(false);
  };

  const handleCourseAdd = (course: CourseCatalog) => {
    onCourseAdd?.(course);
  };

  const isCourseSelected = (course: CourseCatalog) => {
    return selectedCourses.some(
      selected => selected.subject === course.subject && selected.number === course.number
    );
  };

  const formatCourseOption = (course: CourseCatalog) => (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
          {course.subject} {course.number}
        </Typography>
        {course.credit_hours && (
          <Chip 
            label={`${course.credit_hours} credits`} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
        )}
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {course.title}
      </Typography>
      {course.description && (
        <Typography variant="caption" color="text.secondary" sx={{ 
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}>
          {course.description}
        </Typography>
      )}
    </Box>
  );

  const renderCourseCard = (course: CourseCatalog) => (
    <Card key={`${course.subject}-${course.number}`} sx={{ mb: 1 }}>
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {course.subject} {course.number}
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              {course.title}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {course.credit_hours && (
              <Chip 
                label={`${course.credit_hours} credits`} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            )}
            {course.sections.length > 0 && (
              <Chip 
                label={`${course.sections.length} sections`} 
                size="small" 
                color="secondary" 
                variant="outlined"
              />
            )}
          </Box>
        </Box>
        
        {course.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {course.description}
          </Typography>
        )}

        {course.sections.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Available Sections:
            </Typography>
            <Grid container spacing={1}>
              {course.sections.slice(0, 3).map((section, index) => (
                <Grid item xs={12} sm={6} md={4} key={section.id}>
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
              {course.sections.length > 3 && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">
                    +{course.sections.length - 3} more sections
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </CardContent>
      
      <CardActions sx={{ pt: 0, pb: 1, px: 2 }}>
        <Button
          size="small"
          startIcon={<Info />}
          onClick={() => handleCourseSelect(course)}
        >
          View Details
        </Button>
        {showAddButton && !isCourseSelected(course) && (
          <Button
            size="small"
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleCourseAdd(course)}
          >
            Add Course
          </Button>
        )}
        {isCourseSelected(course) && (
          <Chip 
            label="Already Added" 
            size="small" 
            color="success" 
            variant="outlined"
          />
        )}
      </CardActions>
    </Card>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Autocomplete
        open={isOpen}
        onOpen={() => setIsOpen(true)}
        onClose={() => setIsOpen(false)}
        options={courses}
        loading={loadingCourses}
        getOptionLabel={(course) => `${course.subject} ${course.number}: ${course.title}`}
        renderOption={(props, course) => (
          <li {...props}>
            {formatCourseOption(course)}
          </li>
        )}
        renderInput={(params) => (
          <TextField
            {...params}
            placeholder={placeholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
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
        filterOptions={(options) => options} // We handle filtering in the API
        isOptionEqualToValue={(option, value) => 
          option.subject === value.subject && option.number === value.number
        }
        onInputChange={(_, value) => setSearchQuery(value)}
        onChange={(_, value) => value && handleCourseSelect(value)}
        sx={{ mb: 2 }}
      />

      {error && (
        <Alert 
          severity="error" 
          onClose={clearError}
          sx={{ mb: 2 }}
        >
          {error}
        </Alert>
      )}

      {courses.length > 0 && searchQuery.trim() && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Search Results ({courses.length})
            </Typography>
            <Tooltip title="Clear search">
              <IconButton 
                size="small" 
                onClick={() => {
                  setSearchQuery('');
                  setIsOpen(false);
                }}
              >
                ×
              </IconButton>
            </Tooltip>
          </Box>
          
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {courses.slice(0, maxResults).map(renderCourseCard)}
            {courses.length > maxResults && (
              <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', display: 'block', mt: 2 }}>
                Showing first {maxResults} results. Refine your search for more specific results.
              </Typography>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default CourseSearch;
