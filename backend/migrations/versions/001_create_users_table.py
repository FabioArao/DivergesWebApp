"""create users table

Revision ID: 001
Revises: 
Create Date: 2023-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum type for user roles
    op.execute("CREATE TYPE user_role AS ENUM ('student', 'teacher', 'guardian', 'admin')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('firebase_uid', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('student', 'teacher', 'guardian', 'admin', name='user_role'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('profile_picture', sa.String(), nullable=True),
        sa.Column('grade_level', sa.String(), nullable=True),
        sa.Column('subjects', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('firebase_uid'),
        sa.UniqueConstraint('email')
    )
    
    # Create index on firebase_uid for faster lookups
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'])
    
    # Create index on email for faster lookups
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Create index on role for filtering
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Create guardian-student relationship table
    op.create_table(
        'guardian_student',
        sa.Column('guardian_id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['guardian_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('guardian_id', 'student_id')
    )
    
    # Create teacher-student relationship table
    op.create_table(
        'teacher_student',
        sa.Column('teacher_id', sa.String(), nullable=False),
        sa.Column('student_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('teacher_id', 'student_id')
    )
    
    # Create indexes for relationship tables
    op.create_index('idx_guardian_student_guardian_id', 'guardian_student', ['guardian_id'])
    op.create_index('idx_guardian_student_student_id', 'guardian_student', ['student_id'])
    op.create_index('idx_teacher_student_teacher_id', 'teacher_student', ['teacher_id'])
    op.create_index('idx_teacher_student_student_id', 'teacher_student', ['student_id'])

def downgrade():
    # Drop relationship tables and their indexes
    op.drop_table('teacher_student')
    op.drop_table('guardian_student')
    
    # Drop users table and its indexes
    op.drop_table('users')
    
    # Drop the user_role enum type
    op.execute('DROP TYPE user_role')
