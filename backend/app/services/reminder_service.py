"""
Reminder Service

Handles dispatching study session reminders to users based on their notification
preferences.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from ..auth.email_service import EmailService
from ..models import StudySession, StudySessionReminder, User

logger = logging.getLogger(__name__)


class ReminderService:
    """Service responsible for sending study session reminders."""

    def __init__(self, db: Session):
        self.db = db

    def _get_candidate_sessions(
        self,
        within_minutes: int,
        target_user_id: Optional[int] = None,
    ) -> List[StudySession]:
        """Fetch study sessions that start within the configured time window."""
        now = datetime.utcnow()
        upper_bound = now + timedelta(minutes=within_minutes)

        query = (
            self.db.query(StudySession)
            .options(
                joinedload(StudySession.user),
                joinedload(StudySession.assignment),
                joinedload(StudySession.reminder_log),
            )
            .join(User)
            .filter(
                User.reminders_enabled.is_(True),
                StudySession.is_completed.is_(False),
                StudySession.start_time >= now,
                StudySession.start_time <= upper_bound,
            )
        )

        if target_user_id is not None:
            query = query.filter(StudySession.user_id == target_user_id)

        return query.all()

    def _filter_sessions_ready_for_reminder(
        self,
        sessions: List[StudySession],
    ) -> List[Tuple[StudySession, int]]:
        """Determine which sessions should receive a reminder right now."""
        ready: List[Tuple[StudySession, int]] = []
        now = datetime.utcnow()

        for session in sessions:
            user: User = session.user
            lead_minutes = user.reminder_lead_minutes or 30
            minutes_until_session = (session.start_time - now).total_seconds() / 60

            # Reminder criteria:
            # - Session starts within the user's lead time window
            # - Reminder has not been sent yet (no reminder log entry)
            if minutes_until_session <= lead_minutes and not session.reminder_log:
                ready.append((session, lead_minutes))

        return ready

    def send_upcoming_session_reminders(
        self,
        within_minutes: int = 120,
        target_user_id: Optional[int] = None,
        dry_run: bool = False,
    ) -> List[dict]:
        """
        Send reminders for sessions starting soon.

        Args:
            within_minutes: Global search window for upcoming sessions.
            target_user_id: Restrict reminders to a single user (used for testing).
            dry_run: If True, don't persist reminder logs (allows repeated tests).

        Returns:
            A list of dictionaries describing the reminders that were (or would be) sent.
        """
        candidates = self._get_candidate_sessions(within_minutes, target_user_id)
        sessions_ready = self._filter_sessions_ready_for_reminder(candidates)

        results: List[dict] = []

        for session, lead_minutes in sessions_ready:
            try:
                EmailService.send_study_session_reminder(
                    email=session.user.email,
                    session=session,
                    lead_minutes=lead_minutes,
                )

                results.append(
                    {
                        "study_session_id": session.id,
                        "user_id": session.user_id,
                        "assignment_title": session.assignment.title
                        if session.assignment
                        else None,
                        "start_time": session.start_time.isoformat(),
                        "lead_minutes": lead_minutes,
                    }
                )

                if not dry_run:
                    reminder_log = StudySessionReminder(study_session_id=session.id)
                    self.db.add(reminder_log)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Failed to send reminder for session %s: %s", session.id, exc
                )

        if not dry_run and sessions_ready:
            self.db.commit()

        return results

