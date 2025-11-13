import React from 'react';
import { screen, render } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

describe('Dashboard Component', () => {
  it('renders Dashboard heading', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});
