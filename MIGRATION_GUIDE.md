# Database Migration Guide

## Overview
This guide will help you set up Alembic migrations and migrate your database schema to include the new Application management system.

## Prerequisites
1. Make sure you have Alembic installed:
   ```bash
   pip install alembic
   ```

2. Ensure your `.env` file has the correct `DATABASE_URL`:
   ```
   DATABASE_URL=postgresql://username:password@localhost/database_name
   # or for SQLite:
   DATABASE_URL=sqlite:///./resume_maker.db
   ```

## Step-by-Step Migration Process

### Step 1: Initialize Alembic (if not done already)
The Alembic configuration files have already been created for you:
- `alembic.ini` - Main configuration file
- `alembic/env.py` - Environment configuration
- `alembic/script.py.mako` - Migration template
- `alembic/versions/` - Directory for migration files

### Step 2: Create Initial Migration
Run this command to create your first migration with all current models:

```bash
# Navigate to your project directory
cd D:\github\resume_maker_backend

# Create the initial migration
alembic revision --autogenerate -m "Initial migration with all models"
```

This will create a migration file in `alembic/versions/` that includes all your models:
- User
- UserProfile
- UserExperience, UserEducation, UserSkill, UserCertification, UserProject
- Resume
- Experience, Education, Skill, Certification, Project
- Application (with new enhanced fields)
- ApplicationStatusHistory

### Step 3: Review the Generated Migration
Check the generated migration file in `alembic/versions/` to ensure it looks correct. It should include:

```python
def upgrade() -> None:
    # Create all tables
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # ... more table creation statements
    
    # Create applications table with new fields
    op.create_table('applications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('resume_id', sa.UUID(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('job_description', sa.String(), nullable=True),
        sa.Column('application_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('salary_range', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create application status history table
    op.create_table('application_status_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
```

### Step 4: Run the Migration
Apply the migration to your database:

```bash
# Run the migration
alembic upgrade head
```

This will create all the tables in your database.

### Step 5: Verify Migration Status
Check that the migration was applied successfully:

```bash
# Check current migration status
alembic current

# Show migration history
alembic history --verbose
```

## For Existing Databases

If you already have some tables in your database, you have two options:

### Option A: Fresh Start (Recommended for Development)
1. Drop your existing database or delete the SQLite file
2. Run the migration as described above

### Option B: Incremental Migration (For Production)
If you have existing data you want to preserve:

1. First, create a baseline migration for existing tables:
   ```bash
   alembic revision -m "Baseline migration"
   ```

2. Edit the generated migration file to only include the NEW tables/columns:
   - Remove existing table creation statements
   - Keep only the new `applications` and `application_status_history` tables
   - Add any new columns to existing tables

3. Mark the baseline as applied (without running it):
   ```bash
   alembic stamp head
   ```

4. Create a new migration for the application system:
   ```bash
   alembic revision --autogenerate -m "Add application management system"
   ```

5. Run the new migration:
   ```bash
   alembic upgrade head
   ```

## Common Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# Check current migration status
alembic current

# Show migration history
alembic history

# Rollback to specific revision
alembic downgrade <revision_id>

# Generate SQL without applying (dry run)
alembic upgrade head --sql
```

## Troubleshooting

### Error: "Can't locate revision identified by..."
This usually means your database is out of sync. Try:
```bash
alembic stamp head
```

### Error: "Target database is not up to date"
Run:
```bash
alembic upgrade head
```

### Error: "Multiple heads detected"
Merge the migrations:
```bash
alembic merge heads -m "Merge migrations"
```

### Error: Import issues in env.py
Make sure your project directory is in the Python path and all dependencies are installed.

## After Migration

Once your migration is complete, you can:

1. **Test the API endpoints** using the Application Management System
2. **Create test data** to verify everything works
3. **Use the new features**:
   - Create job applications
   - Optimize resumes for specific jobs
   - Track application status
   - View analytics

## Next Steps

1. Run the migration commands above
2. Test your API endpoints with tools like Postman or curl
3. Check that all relationships work correctly
4. Consider adding indexes for better performance:
   ```bash
   alembic revision -m "Add indexes"
   ```

Remember to always backup your database before running migrations in production!
