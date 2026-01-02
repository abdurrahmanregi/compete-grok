import pytest
from agents.schemas import VerifierOutput, VerifiedCitation

def test_verifier_output_schema_paper():
    """Test VerifierOutput with a paper citation."""
    data = {
        "citations": [
            {
                "paper_id": 1,
                "title": "Test Paper",
                "status": "verified"
            }
        ]
    }
    output = VerifierOutput(**data)
    assert len(output.citations) == 1
    assert output.citations[0].paper_id == 1
    assert output.citations[0].title == "Test Paper"
    assert output.citations[0].status == "verified"
    assert output.citations[0].case_id is None

def test_verifier_output_schema_case():
    """Test VerifierOutput with a case citation."""
    data = {
        "citations": [
            {
                "case_id": 101,
                "title": "Test Case v. United States",
                "court": "Supreme Court",
                "holding": "Test holding",
                "status": "verified"
            }
        ]
    }
    output = VerifierOutput(**data)
    assert len(output.citations) == 1
    assert output.citations[0].case_id == 101
    assert output.citations[0].title == "Test Case v. United States"
    assert output.citations[0].court == "Supreme Court"
    assert output.citations[0].holding == "Test holding"
    assert output.citations[0].paper_id is None

def test_verifier_output_schema_mixed():
    """Test VerifierOutput with both paper and case citations."""
    data = {
        "citations": [
            {
                "paper_id": 1,
                "title": "Test Paper",
                "status": "verified"
            },
            {
                "case_id": 101,
                "title": "Test Case",
                "court": "Supreme Court",
                "status": "unverified",
                "reason": "Could not find source"
            }
        ]
    }
    output = VerifierOutput(**data)
    assert len(output.citations) == 2
    assert output.citations[0].paper_id == 1
    assert output.citations[1].case_id == 101
    assert output.citations[1].status == "unverified"
    assert output.citations[1].reason == "Could not find source"

if __name__ == "__main__":
    # Manually run tests if executed as a script
    try:
        test_verifier_output_schema_paper()
        print("test_verifier_output_schema_paper passed")
        test_verifier_output_schema_case()
        print("test_verifier_output_schema_case passed")
        test_verifier_output_schema_mixed()
        print("test_verifier_output_schema_mixed passed")
    except Exception as e:
        print(f"Tests failed: {e}")
        exit(1)
