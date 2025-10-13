/**
 * Course Catalog Service
 * 
 * Handles all API calls to the course catalog backend
 */

export interface CourseSection {
  id: number;
  crn: string;
  days: string;
  times: string;
  instructor: string;
  course_catalog_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CourseCatalog {
  id: number;
  subject: string;
  number: string;
  title: string;
  credit_hours?: number;
  description: string;
  semester: string;
  year: number;
  sections: CourseSection[];
  created_at: string;
  updated_at?: string;
}

export interface CourseCatalogSearch {
  subject?: string;
  number?: string;
  title?: string;
  semester?: string;
  year?: number;
}

export interface CatalogStats {
  total_courses: number;
  total_subjects: number;
  total_sections: number;
  by_semester: Array<{
    semester: string;
    year: number;
    count: number;
  }>;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class CourseCatalogService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/course-catalog`;
  }

  /**
   * Get all available subjects
   */
  async getSubjects(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/subjects`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching subjects:', error);
      throw error;
    }
  }

  /**
   * Get courses with optional filtering
   */
  async getCourses(params: {
    skip?: number;
    limit?: number;
    subject?: string;
    number?: string;
    title?: string;
    semester?: string;
    year?: number;
  } = {}): Promise<CourseCatalog[]> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
      if (params.subject) searchParams.append('subject', params.subject);
      if (params.number) searchParams.append('number', params.number);
      if (params.title) searchParams.append('title', params.title);
      if (params.semester) searchParams.append('semester', params.semester);
      if (params.year !== undefined) searchParams.append('year', params.year.toString());

      const url = `${this.baseUrl}/?${searchParams.toString()}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching courses:', error);
      throw error;
    }
  }

  /**
   * Search courses by query string
   */
  async searchCourses(query: string, limit: number = 50): Promise<CourseCatalog[]> {
    try {
      const searchParams = new URLSearchParams({
        q: query,
        limit: limit.toString()
      });

      const response = await fetch(`${this.baseUrl}/search?${searchParams.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error searching courses:', error);
      throw error;
    }
  }

  /**
   * Get a specific course by subject and number
   */
  async getCourse(subject: string, number: string, semester?: string, year?: number): Promise<CourseCatalog> {
    try {
      const searchParams = new URLSearchParams();
      if (semester) searchParams.append('semester', semester);
      if (year !== undefined) searchParams.append('year', year.toString());

      const url = `${this.baseUrl}/${subject}/${number}?${searchParams.toString()}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Course ${subject} ${number} not found`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching course ${subject} ${number}:`, error);
      throw error;
    }
  }

  /**
   * Get sections for a specific course
   */
  async getCourseSections(subject: string, number: string, semester?: string, year?: number): Promise<CourseSection[]> {
    try {
      const searchParams = new URLSearchParams();
      if (semester) searchParams.append('semester', semester);
      if (year !== undefined) searchParams.append('year', year.toString());

      const url = `${this.baseUrl}/${subject}/${number}/sections?${searchParams.toString()}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Course ${subject} ${number} not found`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error fetching sections for ${subject} ${number}:`, error);
      throw error;
    }
  }

  /**
   * Get catalog statistics (admin endpoint)
   */
  async getCatalogStats(): Promise<CatalogStats> {
    try {
      const response = await fetch(`${this.baseUrl}/admin/stats`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching catalog stats:', error);
      throw error;
    }
  }

  /**
   * Refresh course catalog data (admin endpoint)
   */
  async refreshCatalog(year?: number, semester?: string): Promise<any> {
    try {
      const searchParams = new URLSearchParams();
      if (year !== undefined) searchParams.append('year', year.toString());
      if (semester) searchParams.append('semester', semester);

      const url = `${this.baseUrl}/admin/refresh?${searchParams.toString()}`;
      const response = await fetch(url, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error refreshing catalog:', error);
      throw error;
    }
  }

  /**
   * Get courses by subject with pagination
   */
  async getCoursesBySubject(subject: string, page: number = 0, limit: number = 20): Promise<{
    courses: CourseCatalog[];
    hasMore: boolean;
    total: number;
  }> {
    try {
      const skip = page * limit;
      const courses = await this.getCourses({
        subject,
        skip,
        limit: limit + 1 // Get one extra to check if there are more
      });

      const hasMore = courses.length > limit;
      const actualCourses = hasMore ? courses.slice(0, limit) : courses;

      return {
        courses: actualCourses,
        hasMore,
        total: actualCourses.length
      };
    } catch (error) {
      console.error(`Error fetching courses for subject ${subject}:`, error);
      throw error;
    }
  }

  /**
   * Format course display name
   */
  formatCourseName(course: CourseCatalog): string {
    return `${course.subject} ${course.number}: ${course.title}`;
  }

  /**
   * Format course code
   */
  formatCourseCode(course: CourseCatalog): string {
    return `${course.subject} ${course.number}`;
  }
}

// Export singleton instance
export const courseCatalogService = new CourseCatalogService();
export default courseCatalogService;
