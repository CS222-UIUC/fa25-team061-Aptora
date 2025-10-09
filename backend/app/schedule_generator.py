import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from .models import Assignment, AvailabilitySlot, StudySession, User
from .schemas import ScheduleRequest, ScheduleResponse, StudySession as StudySessionSchema


class ScheduleGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_schedule(self, user_id: int, request: ScheduleRequest) -> ScheduleResponse:
        """
        Generate an optimized study schedule for a user within the given date range.
        """
        # Get user's assignments and availability
        assignments = self._get_user_assignments(user_id, request.start_date, request.end_date)
        availability_slots = self._get_user_availability(user_id)
        
        if not assignments or not availability_slots:
            return ScheduleResponse(study_sessions=[], total_hours_scheduled=0, assignments_covered=[])
        
        # Calculate assignment priorities based on due date and difficulty
        priorities = self._calculate_priorities(assignments)
        
        # Generate time slots based on availability
        time_slots = self._generate_time_slots(availability_slots, request.start_date, request.end_date)
        
        # Optimize schedule using clustering algorithm
        optimized_sessions = self._optimize_schedule(assignments, time_slots, priorities)
        
        # Create study sessions
        study_sessions = []
        total_hours = 0
        assignments_covered = set()
        
        for session_data in optimized_sessions:
            session = StudySession(
                start_time=session_data['start_time'],
                end_time=session_data['end_time'],
                user_id=user_id,
                assignment_id=session_data['assignment_id'],
                notes=session_data.get('notes', '')
            )
            self.db.add(session)
            study_sessions.append(session)
            
            duration = (session_data['end_time'] - session_data['start_time']).total_seconds() / 3600
            total_hours += duration
            assignments_covered.add(session_data['assignment_id'])
        
        self.db.commit()
        
        # Convert to response format
        session_schemas = [
            StudySessionSchema(
                id=session.id,
                start_time=session.start_time,
                end_time=session.end_time,
                user_id=session.user_id,
                assignment_id=session.assignment_id,
                is_completed=session.is_completed,
                notes=session.notes,
                created_at=session.created_at,
                updated_at=session.updated_at
            )
            for session in study_sessions
        ]
        
        return ScheduleResponse(
            study_sessions=session_schemas,
            total_hours_scheduled=total_hours,
            assignments_covered=list(assignments_covered)
        )
    
    def _get_user_assignments(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Assignment]:
        """Get user's assignments within the date range."""
        return self.db.query(Assignment).join(Assignment.course).filter(
            Assignment.course.has(user_id=user_id),
            Assignment.due_date >= start_date,
            Assignment.due_date <= end_date,
            Assignment.is_completed == False
        ).all()
    
    def _get_user_availability(self, user_id: int) -> List[AvailabilitySlot]:
        """Get user's availability slots."""
        return self.db.query(AvailabilitySlot).filter(
            AvailabilitySlot.user_id == user_id
        ).all()
    
    def _calculate_priorities(self, assignments: List[Assignment]) -> Dict[int, float]:
        """Calculate priority scores for assignments based on due date and difficulty."""
        priorities = {}
        current_time = datetime.now()
        
        for assignment in assignments:
            # Time urgency (higher for closer due dates)
            days_until_due = (assignment.due_date - current_time).days
            time_urgency = max(0, 10 - days_until_due) / 10
            
            # Difficulty weight
            difficulty_weights = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
            difficulty_weight = difficulty_weights.get(assignment.difficulty.value, 1.0)
            
            # Combined priority score
            priority = time_urgency * difficulty_weight * assignment.estimated_hours
            priorities[assignment.id] = priority
        
        return priorities
    
    def _generate_time_slots(self, availability_slots: List[AvailabilitySlot], 
                           start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate available time slots based on user's availability."""
        time_slots = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
            
            # Find availability for this day
            day_availability = [slot for slot in availability_slots if slot.day_of_week == day_of_week]
            
            for slot in day_availability:
                start_time_str = slot.start_time
                end_time_str = slot.end_time
                
                # Parse time strings
                start_hour, start_min = map(int, start_time_str.split(':'))
                end_hour, end_min = map(int, end_time_str.split(':'))
                
                # Create datetime objects
                slot_start = datetime.combine(current_date, datetime.min.time().replace(
                    hour=start_hour, minute=start_min
                ))
                slot_end = datetime.combine(current_date, datetime.min.time().replace(
                    hour=end_hour, minute=end_min
                ))
                
                # Ensure slot is within the requested date range
                if slot_start >= start_date and slot_end <= end_date:
                    time_slots.append({
                        'start_time': slot_start,
                        'end_time': slot_end,
                        'duration_hours': (slot_end - slot_start).total_seconds() / 3600
                    })
            
            current_date += timedelta(days=1)
        
        return time_slots
    
    def _optimize_schedule(self, assignments: List[Assignment], 
                         time_slots: List[Dict], priorities: Dict[int, float]) -> List[Dict]:
        """Optimize the schedule using a greedy algorithm with clustering."""
        optimized_sessions = []
        remaining_hours = {assignment.id: assignment.estimated_hours for assignment in assignments}
        
        # Sort assignments by priority (highest first)
        sorted_assignments = sorted(assignments, key=lambda x: priorities.get(x.id, 0), reverse=True)
        
        # Sort time slots by start time
        sorted_time_slots = sorted(time_slots, key=lambda x: x['start_time'])
        
        for assignment in sorted_assignments:
            assignment_id = assignment.id
            remaining_time = remaining_hours[assignment_id]
            
            if remaining_time <= 0:
                continue
            
            # Find best time slots for this assignment
            for time_slot in sorted_time_slots:
                if remaining_time <= 0:
                    break
                
                available_duration = time_slot['duration_hours']
                if available_duration <= 0:
                    continue
                
                # Calculate session duration (max 3 hours per session)
                session_duration = min(remaining_time, available_duration, 3.0)
                
                if session_duration >= 0.5:  # Minimum 30 minutes
                    session_start = time_slot['start_time']
                    session_end = session_start + timedelta(hours=session_duration)
                    
                    optimized_sessions.append({
                        'start_time': session_start,
                        'end_time': session_end,
                        'assignment_id': assignment_id,
                        'notes': f"Study session for {assignment.title}"
                    })
                    
                    # Update remaining time
                    remaining_time -= session_duration
                    remaining_hours[assignment_id] = remaining_time
                    
                    # Update time slot availability
                    time_slot['start_time'] = session_end
                    time_slot['duration_hours'] -= session_duration
        
        return optimized_sessions
