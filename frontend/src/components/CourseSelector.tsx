import React, { useState, useEffect } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useCourseCatalog } from '../hooks/useCourseCatalog';
import { CourseCatalog } from '../services/courseCatalogService';

interface CourseSelectorProps {
  value?: CourseCatalog | null;
  onChange: (course: CourseCatalog | null) => void;
  label?: string;
  placeholder?: string;
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  required?: boolean;
}

const CourseSelector: React.FC<CourseSelectorProps> = ({
  value,
  onChange,
  label = "Select Course",
  placeholder = "Search for a course...",
  error = false,
  helperText,
  disabled = false,
  required = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  
  const {
    courses,
    loadingCourses,
    error: catalogError,
    searchCourses,
    clearError,
  } = useCourseCatalog({ autoLoad: false });

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        searchCourses(searchQuery);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchCourses]);

  const handleInputChange = (event: React.SyntheticEvent, newValue: string) => {
    setSearchQuery(newValue);
  };

  const handleChange = (event: React.SyntheticEvent, newValue: CourseCatalog | null) => {
    onChange(newValue);
  };

  const getOptionLabel = (course: CourseCatalog) => {
    return `${course.subject} ${course.number}: ${course.title}`;
  };

  const renderOption = (props: any, course: CourseCatalog) => (
    <li {...props}>
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
        <Typography variant="body2" color="text.secondary">
          {course.title}
        </Typography>
      </Box>
    </li>
  );

  return (
    <Box>
      <Autocomplete
        open={isOpen}
        onOpen={() => setIsOpen(true)}
        onClose={() => setIsOpen(false)}
        options={courses}
        loading={loadingCourses}
        value={value}
        onChange={handleChange}
        onInputChange={handleInputChange}
        getOptionLabel={getOptionLabel}
        renderOption={renderOption}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            placeholder={placeholder}
            error={error}
            helperText={helperText}
            required={required}
            disabled={disabled}
            InputProps={{
              ...params.InputProps,
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
      />
      
      {catalogError && (
        <Alert 
          severity="error" 
          onClose={clearError}
          sx={{ mt: 1 }}
        >
          {catalogError}
        </Alert>
      )}
    </Box>
  );
};

export default CourseSelector;
