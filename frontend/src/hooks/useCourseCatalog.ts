/**
 * Custom hook for course catalog data management
 */

import { useState, useEffect, useCallback } from 'react';
import { courseCatalogService, CourseCatalog, CourseSection } from '../services/courseCatalogService';

export interface UseCourseCatalogOptions {
  subject?: string;
  autoLoad?: boolean;
}

export interface UseCourseCatalogReturn {
  // Data
  subjects: string[];
  courses: CourseCatalog[];
  selectedCourse: CourseCatalog | null;
  sections: CourseSection[];
  
  // Loading states
  loadingSubjects: boolean;
  loadingCourses: boolean;
  loadingCourse: boolean;
  loadingSections: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  loadSubjects: () => Promise<void>;
  loadCourses: (options?: { subject?: string; search?: string }) => Promise<void>;
  loadCourse: (subject: string, number: string) => Promise<void>;
  loadSections: (subject: string, number: string) => Promise<void>;
  searchCourses: (query: string) => Promise<void>;
  clearError: () => void;
  clearCourses: () => void;
  clearSelectedCourse: () => void;
}

export const useCourseCatalog = (options: UseCourseCatalogOptions = {}): UseCourseCatalogReturn => {
  const { subject, autoLoad = true } = options;

  // State
  const [subjects, setSubjects] = useState<string[]>([]);
  const [courses, setCourses] = useState<CourseCatalog[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<CourseCatalog | null>(null);
  const [sections, setSections] = useState<CourseSection[]>([]);
  
  // Loading states
  const [loadingSubjects, setLoadingSubjects] = useState(false);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [loadingCourse, setLoadingCourse] = useState(false);
  const [loadingSections, setLoadingSections] = useState(false);
  
  // Error state
  const [error, setError] = useState<string | null>(null);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Clear courses
  const clearCourses = useCallback(() => {
    setCourses([]);
  }, []);

  // Clear selected course
  const clearSelectedCourse = useCallback(() => {
    setSelectedCourse(null);
    setSections([]);
  }, []);

  // Load subjects
  const loadSubjects = useCallback(async () => {
    try {
      setLoadingSubjects(true);
      setError(null);
      const subjectsData = await courseCatalogService.getSubjects();
      setSubjects(subjectsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load subjects');
    } finally {
      setLoadingSubjects(false);
    }
  }, []);

  // Load courses
  const loadCourses = useCallback(async (options: { subject?: string; search?: string } = {}) => {
    try {
      setLoadingCourses(true);
      setError(null);
      
      let coursesData: CourseCatalog[];
      
      if (options.search) {
        coursesData = await courseCatalogService.searchCourses(options.search);
      } else {
        coursesData = await courseCatalogService.getCourses({
          subject: options.subject || subject,
          limit: 100
        });
      }
      
      setCourses(coursesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load courses');
    } finally {
      setLoadingCourses(false);
    }
  }, [subject]);

  // Load specific course
  const loadCourse = useCallback(async (subjectCode: string, number: string) => {
    try {
      setLoadingCourse(true);
      setError(null);
      const courseData = await courseCatalogService.getCourse(subjectCode, number);
      setSelectedCourse(courseData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load course');
    } finally {
      setLoadingCourse(false);
    }
  }, []);

  // Load sections for a course
  const loadSections = useCallback(async (subjectCode: string, number: string) => {
    try {
      setLoadingSections(true);
      setError(null);
      const sectionsData = await courseCatalogService.getCourseSections(subjectCode, number);
      setSections(sectionsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sections');
    } finally {
      setLoadingSections(false);
    }
  }, []);

  // Search courses
  const searchCourses = useCallback(async (query: string) => {
    if (!query.trim()) {
      setCourses([]);
      return;
    }
    
    try {
      setLoadingCourses(true);
      setError(null);
      const coursesData = await courseCatalogService.searchCourses(query);
      setCourses(coursesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search courses');
    } finally {
      setLoadingCourses(false);
    }
  }, []);

  // Auto-load subjects on mount
  useEffect(() => {
    if (autoLoad) {
      loadSubjects();
    }
  }, [autoLoad, loadSubjects]);

  // Auto-load courses when subject changes
  useEffect(() => {
    if (subject && autoLoad) {
      loadCourses({ subject });
    }
  }, [subject, autoLoad, loadCourses]);

  return {
    // Data
    subjects,
    courses,
    selectedCourse,
    sections,
    
    // Loading states
    loadingSubjects,
    loadingCourses,
    loadingCourse,
    loadingSections,
    
    // Error state
    error,
    
    // Actions
    loadSubjects,
    loadCourses,
    loadCourse,
    loadSections,
    searchCourses,
    clearError,
    clearCourses,
    clearSelectedCourse,
  };
};

export default useCourseCatalog;
