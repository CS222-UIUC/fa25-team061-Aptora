import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  CalendarToday, 
  CheckCircle, 
  Assignment, 
  TrendingUp,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import dayjs from 'dayjs';

interface ProgressData {
  assignments: {
    total: number;
    completed: number;
    percent: number;
  };
  study_sessions: {
    total: number;
    completed: number;
    percent: number;
  };
}

interface StudySession {
  id: number;
  start_time: string;
  end_time: string;
  assignment_id: number;
  is_completed: boolean;
  notes?: string;
}

interface Assignment {
  id: number;
  title: string;
  due_date: string;
  is_completed: boolean;
  estimated_hours: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Fetch progress statistics
  const { data: progressData, isLoading: progressLoading } = useQuery<ProgressData>(
    'progress',
    async () => {
      const response = await axios.get('/progress/');
      return response.data;
    },
    {
      enabled: !!user,
      refetchOnWindowFocus: true,
    }
  );

  // Fetch study sessions
  const { data: studySessions, isLoading: sessionsLoading } = useQuery<StudySession[]>(
    'study-sessions',
    async () => {
      const response = await axios.get('/schedules/sessions');
      return response.data;
    },
    {
      enabled: !!user,
      refetchOnWindowFocus: true,
    }
  );

  // Fetch assignments
  const { data: assignments, isLoading: assignmentsLoading } = useQuery<Assignment[]>(
    'assignments',
    async () => {
      const response = await axios.get('/assignments/');
      return response.data;
    },
    {
      enabled: !!user,
      refetchOnWindowFocus: true,
    }
  );

  // Calculate statistics from real data
  const stats = useMemo(() => {
    const now = new Date();
    const endOfWeek = new Date(now);
    endOfWeek.setDate(now.getDate() + (7 - now.getDay())); // End of current week (Sunday)
    endOfWeek.setHours(23, 59, 59, 999);

    // Upcoming sessions (not completed, start_time in the future)
    const upcomingSessions = studySessions?.filter(session => {
      const startTime = new Date(session.start_time);
      return !session.is_completed && startTime > now;
    }).length || 0;

    // Completed sessions
    const completedSessions = progressData?.study_sessions.completed || 0;

    // Tasks due this week
    const tasksDueThisWeek = assignments?.filter(assignment => {
      if (assignment.is_completed) return false;
      const dueDate = new Date(assignment.due_date);
      return dueDate >= now && dueDate <= endOfWeek;
    }).length || 0;

    // Calculate productivity score based on completion rates
    const assignmentCompletionRate = progressData?.assignments.percent || 0;
    const sessionCompletionRate = progressData?.study_sessions.percent || 0;
    const productivityScore = Math.round((assignmentCompletionRate + sessionCompletionRate) / 2);

    return {
      upcomingSessions,
      completedSessions,
      tasksDue: tasksDueThisWeek,
      productivityScore: productivityScore || 0,
    };
  }, [studySessions, progressData, assignments]);

  // Generate productivity data for last 7 days
  const productivityData = useMemo(() => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const data = days.map((day, index) => {
      const date = dayjs().subtract(6 - index, 'day');
      const startOfDay = date.startOf('day').toDate();
      const endOfDay = date.endOf('day').toDate();

      // Count completed sessions for this day
      const sessionsOnDay = studySessions?.filter(session => {
        if (!session.is_completed) return false;
        const sessionDate = new Date(session.start_time);
        return sessionDate >= startOfDay && sessionDate <= endOfDay;
      }).length || 0;

      // Calculate productivity (sessions completed / total sessions scheduled for that day)
      const totalSessionsOnDay = studySessions?.filter(session => {
        const sessionDate = new Date(session.start_time);
        return sessionDate >= startOfDay && sessionDate <= endOfDay;
      }).length || 0;

      const productivity = totalSessionsOnDay > 0 
        ? Math.round((sessionsOnDay / totalSessionsOnDay) * 100)
        : 0;

      return {
        date: day,
        productivity: productivity || 0,
      };
    });

    return data;
  }, [studySessions]);

  // Task completion breakdown
  const taskCompletionData = useMemo(() => {
    const completed = progressData?.assignments.completed || 0;
    const pending = (progressData?.assignments.total || 0) - completed;
    return [
      { name: 'Completed', value: completed },
      { name: 'Pending', value: pending },
    ];
  }, [progressData]);

  const COLORS = ['#6366f1', '#ec4899'];

  const cardStyles: React.CSSProperties = {
    background: 'white',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  };

  const statCardStyles: React.CSSProperties[] = [
    {
      ...cardStyles,
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
    },
    {
      ...cardStyles,
      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      color: 'white',
    },
    {
      ...cardStyles,
      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      color: 'white',
    },
    {
      ...cardStyles,
      background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      color: 'white',
    },
  ];

  const isLoading = progressLoading || sessionsLoading || assignmentsLoading;

  // Generate weekly overview text
  const weeklyOverview = useMemo(() => {
    const completedCount = stats.completedSessions;
    const upcomingCount = stats.upcomingSessions;
    const tasksCount = stats.tasksDue;
    const pendingTasks = (progressData?.assignments.total || 0) - (progressData?.assignments.completed || 0);
    const score = stats.productivityScore;

    let message = `This week has been `;
    if (score >= 80) {
      message += 'highly productive';
    } else if (score >= 60) {
      message += 'productive';
    } else if (score >= 40) {
      message += 'moderately productive';
    } else {
      message += 'a slow start';
    }

    message += ` with ${completedCount} completed study session${completedCount !== 1 ? 's' : ''}`;
    if (upcomingCount > 0) {
      message += ` and ${upcomingCount} upcoming session${upcomingCount !== 1 ? 's' : ''} scheduled`;
    }
    message += `. Your productivity score of ${score} indicates `;
    
    if (score >= 80) {
      message += 'excellent performance. ';
    } else if (score >= 60) {
      message += 'consistent performance. ';
    } else if (score >= 40) {
      message += 'room for improvement. ';
    } else {
      message += 'you should focus on completing more tasks. ';
    }

    if (tasksCount > 0) {
      message += `You have ${tasksCount} task${tasksCount !== 1 ? 's' : ''} due this week`;
      if (pendingTasks > 0) {
        message += `, with ${pendingTasks} task${pendingTasks !== 1 ? 's' : ''} still pending`;
      }
      message += '. ';
    }

    message += 'Keep up the great work and maintain your study momentum!';

    return message;
  }, [stats, progressData]);

  if (isLoading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: '#f5f7fa',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#718096', fontSize: '18px' }}>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#f5f7fa',
      padding: '16px 24px'
    }}>
      <div style={{ 
        maxWidth: '1280px', 
        margin: '0 auto',
        padding: '0'
      }}>
        {/* Page Header */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '32px', 
            fontWeight: 700, 
            color: '#1a202c',
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>
            Dashboard
          </h1>
          <p style={{ 
            color: '#718096', 
            fontSize: '14px',
            margin: 0
          }}>
            Your study insights and progress overview
          </p>
        </div>

        {/* Statistics Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {/* Upcoming Sessions Card */}
          <div 
            style={statCardStyles[0]}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <CalendarToday style={{ fontSize: '32px', opacity: 0.9 }} />
              <ArrowUpward style={{ fontSize: '20px', opacity: 0.8 }} />
            </div>
            <h3 style={{ 
              fontSize: '14px', 
              fontWeight: 500, 
              opacity: 0.9,
              margin: '0 0 8px 0'
            }}>
              Upcoming Sessions
            </h3>
            <p style={{ 
              fontSize: '36px', 
              fontWeight: 700,
              margin: 0
            }}>
              {stats.upcomingSessions}
            </p>
          </div>

          {/* Completed Sessions Card */}
          <div 
            style={statCardStyles[1]}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <CheckCircle style={{ fontSize: '32px', opacity: 0.9 }} />
              <TrendingUp style={{ fontSize: '20px', opacity: 0.8 }} />
            </div>
            <h3 style={{ 
              fontSize: '14px', 
              fontWeight: 500, 
              opacity: 0.9,
              margin: '0 0 8px 0'
            }}>
              Completed Sessions
            </h3>
            <p style={{ 
              fontSize: '36px', 
              fontWeight: 700,
              margin: 0
            }}>
              {stats.completedSessions}
            </p>
          </div>

          {/* Tasks Due This Week Card */}
          <div 
            style={statCardStyles[2]}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <Assignment style={{ fontSize: '32px', opacity: 0.9 }} />
              <ArrowDownward style={{ fontSize: '20px', opacity: 0.8 }} />
            </div>
            <h3 style={{ 
              fontSize: '14px', 
              fontWeight: 500, 
              opacity: 0.9,
              margin: '0 0 8px 0'
            }}>
              Tasks Due This Week
            </h3>
            <p style={{ 
              fontSize: '36px', 
              fontWeight: 700,
              margin: 0
            }}>
              {stats.tasksDue}
            </p>
          </div>

          {/* Productivity Score Card */}
          <div 
            style={statCardStyles[3]}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <TrendingUp style={{ fontSize: '32px', opacity: 0.9 }} />
              <ArrowUpward style={{ fontSize: '20px', opacity: 0.8 }} />
            </div>
            <h3 style={{ 
              fontSize: '14px', 
              fontWeight: 500, 
              opacity: 0.9,
              margin: '0 0 8px 0'
            }}>
              Productivity Score
            </h3>
            <p style={{ 
              fontSize: '36px', 
              fontWeight: 700,
              margin: 0
            }}>
              {stats.productivityScore}
            </p>
          </div>
        </div>

        {/* Charts Section */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {/* Productivity Over Time */}
          <div style={cardStyles}>
            <h2 style={{ 
              fontSize: '20px', 
              fontWeight: 600, 
              color: '#1a202c',
              marginBottom: '24px',
              margin: '0 0 24px 0'
            }}>
              Productivity Over Time
            </h2>
            <div style={{ width: '100%', height: '300px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={productivityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#718096"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    stroke="#718096"
                    style={{ fontSize: '12px' }}
                    domain={[0, 100]}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="productivity"
                    stroke="#6366f1"
                    strokeWidth={3}
                    name="Productivity %"
                    dot={{ fill: '#6366f1', r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Task Completion Breakdown */}
          <div style={cardStyles}>
            <h2 style={{ 
              fontSize: '20px', 
              fontWeight: 600, 
              color: '#1a202c',
              marginBottom: '24px',
              margin: '0 0 24px 0'
            }}>
              Task Completion Breakdown
            </h2>
            <div style={{ width: '100%', height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              {taskCompletionData[0].value === 0 && taskCompletionData[1].value === 0 ? (
                <p style={{ color: '#718096', fontSize: '16px' }}>No tasks yet</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={taskCompletionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {taskCompletionData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        {/* Weekly Overview */}
        <div style={cardStyles}>
          <h2 style={{ 
            fontSize: '20px', 
            fontWeight: 600, 
            color: '#1a202c',
            marginBottom: '16px',
            margin: '0 0 16px 0'
          }}>
            Weekly Overview
          </h2>
          <p style={{ 
            color: '#4a5568', 
            lineHeight: '1.75',
            fontSize: '16px',
            margin: 0
          }}>
            {weeklyOverview}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
