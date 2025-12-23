"""
Tests for database seeding functionality
"""
import pytest
import json
from pathlib import Path
from app.models import Program, Course, Requirement, TrackRequirement, Embedding


@pytest.mark.seeding
@pytest.mark.integration
class TestSeeding:
    """Test database seeding functions"""

    def test_load_json(self):
        """Test JSON loading function"""
        from scripts.seed_database import load_json

        # Create a temporary JSON file
        test_data = {"test": "data"}
        test_file = Path("/tmp/test_seed.json")
        test_file.write_text(json.dumps(test_data))

        try:
            result = load_json(str(test_file))
            assert result == test_data
        finally:
            test_file.unlink()

    def test_create_embedding_text_course(self):
        """Test embedding text creation for courses"""
        from scripts.seed_database import create_embedding_text

        course_data = {
            "program_id": "rice-bioe-2025",
            "code": "BIOE 252",
            "title": "Introduction to Bioengineering",
            "credits": 3,
            "terms": ["Fall", "Spring"],
            "prereqs": ["MATH 212"],
            "tags": ["core"],
            "description": "Intro course",
            "source_url": "https://example.com",
        }

        text = create_embedding_text("course", course_data)
        assert "[TYPE] Course" in text
        assert "BIOE 252" in text
        assert "Introduction to Bioengineering" in text
        assert "rice-bioe-2025" in text

    def test_create_embedding_text_requirement(self):
        """Test embedding text creation for requirements"""
        from scripts.seed_database import create_embedding_text

        req_data = {
            "program_id": "rice-bioe-2025",
            "requirement_id": "req-1",
            "type": "AND",
            "rules": [{"type": "COURSE", "code": "BIOE 252"}],
            "description": "Core requirement",
            "text_source": "Catalog",
            "source_url": "https://example.com",
        }

        text = create_embedding_text("requirement", req_data)
        assert "[TYPE] Requirement" in text
        assert "req-1" in text
        assert "rice-bioe-2025" in text

    def test_seed_programs(self, db_session):
        """Test seeding programs"""
        from scripts.seed_database import seed_programs

        # Create a temporary programs.json
        test_data = [
            {
                "program_id": "test-program",
                "university": "Test University",
                "degree": "BS",
                "major": "Test Major",
                "catalog_url": "https://example.com",
                "version_year": 2025,
            }
        ]
        data_dir = Path("/tmp")
        programs_file = data_dir / "seed" / "programs.json"
        programs_file.parent.mkdir(parents=True, exist_ok=True)
        programs_file.write_text(json.dumps(test_data))

        try:
            seed_programs(db_session, data_dir)
            db_session.commit()

            program = db_session.query(Program).filter(
                Program.program_id == "test-program"
            ).first()
            assert program is not None
            assert program.university == "Test University"
        finally:
            programs_file.unlink()
            programs_file.parent.rmdir()

