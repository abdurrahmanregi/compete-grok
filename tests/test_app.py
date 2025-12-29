import pytest
from app import fix_md_math

def test_fix_md_math():
    # Test the fix_md_math function
    md_content = r"""
Some text

\[ E = mc^2 \]

More text
"""
    # Create a temp file
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(md_content)
        temp_path = f.name

    try:
        fixed_path = fix_md_math(temp_path)
        with open(fixed_path, 'r') as f:
            fixed_content = f.read()
        assert r'\[ E = mc^2 \]' not in fixed_content  # Should be dedented
        assert 'E = mc^2' in fixed_content
    finally:
        os.unlink(temp_path)
        if os.path.exists(fixed_path):
            os.unlink(fixed_path)

if __name__ == "__main__":
    test_fix_md_math()
    print("Test passed")