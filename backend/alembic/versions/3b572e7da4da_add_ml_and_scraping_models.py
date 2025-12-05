"""Add ML and scraping models

Revision ID: 3b572e7da4da
Revises: 3bee30da6f37
Create Date: 2025-12-04 19:29:27.093161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b572e7da4da'
down_revision = '3bee30da6f37'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create professor_ratings table
    op.create_table(
        'professor_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('professor_name', sa.String(), nullable=False),
        sa.Column('course_subject', sa.String(), nullable=False),
        sa.Column('course_number', sa.String(), nullable=False),
        sa.Column('overall_rating', sa.Float(), nullable=True),
        sa.Column('difficulty_rating', sa.Float(), nullable=True),
        sa.Column('would_take_again_percent', sa.Float(), nullable=True),
        sa.Column('source', sa.Enum('RATEMYPROFESSOR', 'REDDIT', 'COURSE_REVIEW', 'COURSE_FORUM', name='scrapersource'), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professor_ratings_id'), 'professor_ratings', ['id'], unique=False)
    op.create_index(op.f('ix_professor_ratings_professor_name'), 'professor_ratings', ['professor_name'], unique=False)

    # Create course_insights table
    op.create_table(
        'course_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_subject', sa.String(), nullable=False),
        sa.Column('course_number', sa.String(), nullable=False),
        sa.Column('avg_hours_per_week', sa.Float(), nullable=True),
        sa.Column('difficulty_score', sa.Float(), nullable=True),
        sa.Column('workload_rating', sa.Float(), nullable=True),
        sa.Column('assignment_frequency', sa.String(), nullable=True),
        sa.Column('exam_count', sa.Integer(), nullable=True),
        sa.Column('source', sa.Enum('RATEMYPROFESSOR', 'REDDIT', 'COURSE_REVIEW', 'COURSE_FORUM', name='scrapersource'), nullable=False),
        sa.Column('semester', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_insights_id'), 'course_insights', ['id'], unique=False)
    op.create_index(op.f('ix_course_insights_course_subject'), 'course_insights', ['course_subject'], unique=False)
    op.create_index(op.f('ix_course_insights_course_number'), 'course_insights', ['course_number'], unique=False)

    # Create assignment_patterns table
    op.create_table(
        'assignment_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_subject', sa.String(), nullable=False),
        sa.Column('course_number', sa.String(), nullable=False),
        sa.Column('assignment_type', sa.Enum('ASSIGNMENT', 'EXAM', 'PROJECT', name='tasktype'), nullable=False),
        sa.Column('typical_duration_hours', sa.Float(), nullable=True),
        sa.Column('difficulty_avg', sa.Float(), nullable=True),
        sa.Column('student_feedback_count', sa.Integer(), nullable=True),
        sa.Column('source', sa.Text(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignment_patterns_id'), 'assignment_patterns', ['id'], unique=False)

    # Create ml_models table
    op.create_table(
        'ml_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.Enum('TIME_ESTIMATOR', 'SCHEDULER_POLICY', name='mlmodeltype'), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('model_path', sa.String(), nullable=False),
        sa.Column('metrics', sa.Text(), nullable=True),
        sa.Column('training_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('feature_importance', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_models_id'), 'ml_models', ['id'], unique=False)

    # Create study_time_predictions table
    op.create_table(
        'study_time_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('predicted_hours', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('features_used', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_time_predictions_id'), 'study_time_predictions', ['id'], unique=False)

    # Create study_session_feedback table
    op.create_table(
        'study_session_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_session_id', sa.Integer(), nullable=False),
        sa.Column('actual_duration_hours', sa.Float(), nullable=True),
        sa.Column('productivity_rating', sa.Float(), nullable=True),
        sa.Column('difficulty_rating', sa.Float(), nullable=True),
        sa.Column('was_sufficient', sa.Boolean(), nullable=True),
        sa.Column('student_comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['study_session_id'], ['study_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_session_feedback_id'), 'study_session_feedback', ['id'], unique=False)

    # Create scraper_jobs table
    op.create_table(
        'scraper_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(), nullable=False),
        sa.Column('target_identifier', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_scraped', sa.Integer(), nullable=True),
        sa.Column('next_scheduled_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_jobs_id'), 'scraper_jobs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scraper_jobs_id'), table_name='scraper_jobs')
    op.drop_table('scraper_jobs')
    op.drop_index(op.f('ix_study_session_feedback_id'), table_name='study_session_feedback')
    op.drop_table('study_session_feedback')
    op.drop_index(op.f('ix_study_time_predictions_id'), table_name='study_time_predictions')
    op.drop_table('study_time_predictions')
    op.drop_index(op.f('ix_ml_models_id'), table_name='ml_models')
    op.drop_table('ml_models')
    op.drop_index(op.f('ix_assignment_patterns_id'), table_name='assignment_patterns')
    op.drop_table('assignment_patterns')
    op.drop_index(op.f('ix_course_insights_course_number'), table_name='course_insights')
    op.drop_index(op.f('ix_course_insights_course_subject'), table_name='course_insights')
    op.drop_index(op.f('ix_course_insights_id'), table_name='course_insights')
    op.drop_table('course_insights')
    op.drop_index(op.f('ix_professor_ratings_professor_name'), table_name='professor_ratings')
    op.drop_index(op.f('ix_professor_ratings_id'), table_name='professor_ratings')
    op.drop_table('professor_ratings')
