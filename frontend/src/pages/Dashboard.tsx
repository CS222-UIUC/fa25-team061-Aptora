import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  CalendarToday, 
  CheckCircle, 
  Assignment, 
  TrendingUp,
  ArrowUpward,
  ArrowDownward
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  // Mock data for statistics
  const stats = {
    upcomingSessions: 4,
    completedSessions: 12,
    tasksDue: 3,
    productivityScore: 78,
  };

  // Mock data for productivity over time (last 7 days)
  const productivityData = [
    { date: 'Mon', productivity: 65 },
    { date: 'Tue', productivity: 72 },
    { date: 'Wed', productivity: 68 },
    { date: 'Thu', productivity: 80 },
    { date: 'Fri', productivity: 75 },
    { date: 'Sat', productivity: 70 },
    { date: 'Sun', productivity: 78 },
  ];

  // Mock data for task completion breakdown
  const taskCompletionData = [
    { name: 'Completed', value: 12 },
    { name: 'Pending', value: 6 },
  ];

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
                    name="Productivity"
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
            This week has been productive with 12 completed study sessions and
            4 upcoming sessions scheduled. Your productivity score of 78
            indicates consistent performance. You have 3 tasks due this week,
            with 6 tasks still pending. Keep up the great work and maintain your
            study momentum!
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
