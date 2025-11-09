"""
Seed database with course catalog data and generate embeddings
"""
import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.database import SessionLocal, engine, init_db
from app.core.config import settings
from app.models import Base, Program, Course, Requirement, TrackRequirement, Embedding


def load_json(file_path: str):
    """Load JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def create_embedding_text(item_type: str, data: dict) -> str:
    """Create text blob for embedding"""
    if item_type == "course":
        return f"""[TYPE] Course
program_id: {data.get('program_id', '')}
code: {data.get('code', '')}
title: {data.get('title', '')}
credits: {data.get('credits', '')}
terms: {', '.join(data.get('terms', []))}
prereqs: {', '.join(data.get('prereqs', []))}
tags: {', '.join(data.get('tags', []))}
description: {data.get('description', '')}
source_url: {data.get('source_url', '')}"""

    elif item_type == "requirement":
        rules_text = json.dumps(data.get('rules', []))
        return f"""[TYPE] Requirement
program_id: {data.get('program_id', '')}
id: {data.get('requirement_id', '')}
type: {data.get('type', '')}
rules: {rules_text}
description: {data.get('description', '')}
text_source: {data.get('text_source', '')}
source_url: {data.get('source_url', '')}"""

    return ""


def generate_embedding(client: OpenAI, text: str) -> list:
    """Generate embedding using OpenAI API"""
    try:
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def seed_programs(db: Session, data_dir: Path):
    """Seed programs table"""
    print("Seeding programs...")
    programs = load_json(data_dir / "seed" / "programs.json")

    for prog_data in programs:
        program = Program(**prog_data)
        db.add(program)

    db.commit()
    print(f"✓ Seeded {len(programs)} programs")


def seed_courses(db: Session, client: OpenAI, data_dir: Path):
    """Seed courses table and generate embeddings"""
    print("\nSeeding courses...")

    course_files = [
        "courses.rice.json",
        "courses.utexas.json",
        "courses.stanford.json"
    ]

    total_courses = 0
    for file_name in course_files:
        courses = load_json(data_dir / "seed" / file_name)

        for course_data in courses:
            # Add course to database
            course = Course(**course_data)
            db.add(course)
            db.flush()  # Get the ID

            # Generate embedding
            embed_text = create_embedding_text("course", course_data)
            vector = generate_embedding(client, embed_text)

            if vector:
                embedding = Embedding(
                    program_id=course_data['program_id'],
                    type="course",
                    content_text=embed_text,
                    vector=vector,
                    metadata={
                        "code": course_data['code'],
                        "title": course_data['title'],
                        "source_url": course_data.get('source_url', '')
                    }
                )
                db.add(embedding)

            total_courses += 1

        print(f"  ✓ Loaded {file_name}: {len(courses)} courses")

    db.commit()
    print(f"✓ Seeded {total_courses} courses with embeddings")


def seed_requirements(db: Session, client: OpenAI, data_dir: Path):
    """Seed requirements table and generate embeddings"""
    print("\nSeeding requirements...")

    req_files = [
        "requirements.rice.json",
        "requirements.utexas.json",
        "requirements.stanford.json"
    ]

    total_reqs = 0
    for file_name in req_files:
        requirements = load_json(data_dir / "seed" / file_name)

        for req_data in requirements:
            # Add requirement to database
            requirement = Requirement(**req_data)
            db.add(requirement)
            db.flush()

            # Generate embedding
            embed_text = create_embedding_text("requirement", req_data)
            vector = generate_embedding(client, embed_text)

            if vector:
                embedding = Embedding(
                    program_id=req_data['program_id'],
                    type="requirement",
                    content_text=embed_text,
                    vector=vector,
                    metadata={
                        "requirement_id": req_data['requirement_id'],
                        "description": req_data.get('description', ''),
                        "source_url": req_data.get('source_url', '')
                    }
                )
                db.add(embedding)

            total_reqs += 1

        print(f"  ✓ Loaded {file_name}: {len(requirements)} requirements")

    db.commit()
    print(f"✓ Seeded {total_reqs} requirements with embeddings")


def seed_tracks(db: Session, data_dir: Path):
    """Seed track requirements table"""
    print("\nSeeding track requirements...")
    tracks = load_json(data_dir / "seed" / "track_requirements.json")

    for track_data in tracks:
        track = TrackRequirement(**track_data)
        db.add(track)

    db.commit()
    print(f"✓ Seeded {len(tracks)} track requirements")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Navio Database Seeder")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized with pgvector extension")

    # Get data directory
    data_dir = Path(__file__).parent.parent / "data"

    # Initialize OpenAI client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data
        print("\nClearing existing data...")
        db.query(Embedding).delete()
        db.query(Course).delete()
        db.query(Requirement).delete()
        db.query(TrackRequirement).delete()
        db.query(Program).delete()
        db.commit()
        print("✓ Cleared existing data")

        # Seed all tables
        seed_programs(db, data_dir)
        seed_courses(db, client, data_dir)
        seed_requirements(db, client, data_dir)
        seed_tracks(db, data_dir)

        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
