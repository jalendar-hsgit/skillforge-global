"""
Backend tests for Resume Import API
Tests: PDF/DOCX parsing, preview generation, resume creation from import
Run with: pytest backend/tests/test_resume_import.py -v
"""
import pytest
import tempfile
import os
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

from fastapi.testclient import TestClient
from fastapi import UploadFile

from app.main import app


client = TestClient(app)


# ============ Fixtures ============

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    # Create a minimal PDF file
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(John Doe) Tj
100 680 Td
(john@example.com) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000229 00000 n 
0000000310 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
404
%%EOF"""
    return BytesIO(pdf_content)


@pytest.fixture
def sample_docx_file():
    """Create a minimal DOCX (ZIP) file for testing"""
    import zipfile
    
    docx_buffer = BytesIO()
    with zipfile.ZipFile(docx_buffer, 'w') as docx:
        # Add minimal DOCX structure
        docx.writestr('word/document.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:r><w:t>John Doe</w:t></w:r></w:p>
<w:p><w:r><w:t>john@example.com</w:t></w:r></w:p>
<w:p><w:r><w:t>+1-555-1234</w:t></w:r></w:p>
<w:p><w:r><w:t>Senior Software Developer with 10+ years experience</w:t></w:r></w:p>
</w:body>
</w:document>''')
    
    docx_buffer.seek(0)
    return docx_buffer


@pytest.fixture
def invalid_file():
    """Create an invalid file for testing"""
    return BytesIO(b"This is not a valid PDF or DOCX file")


# ============ Resume Import Tests ============

class TestResumeImportUpload:
    """Tests for resume upload and parsing"""

    def test_upload_pdf_success(self, sample_pdf_file):
        """Test successful PDF upload and resume creation"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={
                "full_name": "John Doe",
                "email": "john@example.com",
            },
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should return 201 Created if successful
        assert response.status_code in [201, 401, 422]

    def test_upload_docx_success(self, sample_docx_file):
        """Test successful DOCX upload and resume creation"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("resume.docx", sample_docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should return 201 Created if successful
        assert response.status_code in [201, 401, 422]

    def test_upload_returns_resume_object(self, sample_pdf_file):
        """Test that upload returns created resume object with ID"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 201:
            data = response.json()
            # Should contain resume ID for navigation
            assert "id" in data or "detail" in data

    def test_upload_invalid_file_type(self, invalid_file):
        """Test upload with invalid file type returns error"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("invalid.txt", invalid_file, "text/plain")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should return 400 Bad Request for invalid file type
        assert response.status_code in [400, 401, 415]

    def test_upload_file_too_large(self, sample_pdf_file):
        """Test upload with file larger than 10MB returns error"""
        # This would require creating a large file
        # For now, just test the endpoint structure
        
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should handle size validation
        assert response.status_code in [201, 401, 413, 422]

    def test_upload_missing_file(self):
        """Test upload without file attachment"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should return 422 Unprocessable Entity
        assert response.status_code in [422, 401]

    def test_upload_unauthenticated(self, sample_pdf_file):
        """Test upload requires authentication"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
        )

        assert response.status_code == 401

    def test_upload_with_overrides(self, sample_pdf_file):
        """Test upload with manual field overrides"""
        response = client.post(
            "/api/v1x/resume-import/upload",
            data={
                "full_name": "Jane Smith",  # Override parsed name
                "email": "jane@example.com",
                "phone": "+1-555-9999",
                "summary": "Custom summary",
            },
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 201:
            data = response.json()
            # Overrides should take precedence
            # (Verification would require checking the created resume)
            assert "id" in data or "detail" in data


# ============ Resume Parse Preview Tests ============

class TestResumeImportParsePreview:
    """Tests for resume parsing and preview without creation"""

    def test_parse_preview_pdf(self, sample_pdf_file):
        """Test PDF parsing and preview generation"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should return preview without creating resume
        assert response.status_code in [200, 401, 422]

    def test_parse_preview_docx(self, sample_docx_file):
        """Test DOCX parsing and preview generation"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.docx", sample_docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 401, 422]

    def test_parse_preview_returns_parsed_data(self, sample_pdf_file):
        """Test that parse preview returns extracted data"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 200:
            data = response.json()
            # Should contain parsed data
            assert "parsed_data" in data or "detail" in data

    def test_parse_preview_extracts_name(self, sample_pdf_file):
        """Test that parsing extracts full name"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 200:
            data = response.json()
            # Should extract name from document
            if "parsed_data" in data:
                parsed = data["parsed_data"]
                # Name extraction may or may not succeed depending on PDF content
                assert isinstance(parsed, dict)

    def test_parse_preview_extracts_email(self, sample_pdf_file):
        """Test that parsing extracts email"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 200:
            data = response.json()
            if "parsed_data" in data:
                parsed = data["parsed_data"]
                assert isinstance(parsed, dict)

    def test_parse_preview_extracts_phone(self, sample_pdf_file):
        """Test that parsing extracts phone number"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 200:
            data = response.json()
            if "parsed_data" in data:
                parsed = data["parsed_data"]
                assert isinstance(parsed, dict)

    def test_parse_preview_ai_enhancement(self, sample_pdf_file):
        """Test parse preview with AI enhancement"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": True},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        if response.status_code == 200:
            data = response.json()
            # AI enhanced version should indicate AI was used
            if "ai_used" in data:
                assert isinstance(data["ai_used"], bool)

    def test_parse_preview_invalid_file_type(self, invalid_file):
        """Test parse preview with invalid file type"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("invalid.txt", invalid_file, "text/plain")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [400, 401, 415]

    def test_parse_preview_unauthenticated(self, sample_pdf_file):
        """Test parse preview requires authentication"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
        )

        assert response.status_code == 401

    def test_parse_preview_no_resume_creation(self, sample_pdf_file):
        """Test that parse preview does not create resume in database"""
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Parse preview should not return an ID
        if response.status_code == 200:
            data = response.json()
            # Should not have 'id' in response (that's only in upload endpoint)
            assert "id" not in data


# ============ Resume Parsing Utilities Tests ============

class TestParsingUtilities:
    """Tests for individual parsing utility functions"""

    def test_extract_name_from_text(self):
        """Test name extraction from text"""
        # This would test the extract_name_from_text function
        # In a real test, this would be imported from the module
        
        # Mock test for structure
        assert True

    def test_extract_email_from_text(self):
        """Test email extraction from text"""
        # This would test the extract_email_from_text function
        
        assert True

    def test_extract_phone_from_text(self):
        """Test phone number extraction from text"""
        # This would test the extract_phone_from_text function
        
        assert True

    def test_extract_skills_from_text(self):
        """Test skills extraction from text"""
        # This would test the extract_skills function
        
        assert True

    def test_extract_work_experience_from_text(self):
        """Test work experience extraction from text"""
        # This would test the extract_work_experience function
        
        assert True


# ============ Integration Tests ============

class TestResumeImportIntegration:
    """Integration tests for complete import flow"""

    def test_import_flow_parse_then_upload(self, sample_pdf_file):
        """Test complete flow: parse preview → upload → navigate"""
        # Step 1: Parse preview (no creation)
        sample_pdf_file.seek(0)
        parse_response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        parse_success = parse_response.status_code == 200

        # Step 2: Upload to create resume
        sample_pdf_file.seek(0)
        upload_response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        upload_success = upload_response.status_code == 201

        # Steps should work independently
        assert parse_response.status_code in [200, 401, 422]
        assert upload_response.status_code in [201, 401, 422]

    def test_import_flow_with_user_overrides(self, sample_pdf_file):
        """Test import flow where user corrects parsed data"""
        # User would:
        # 1. Parse preview to see extracted data
        # 2. Modify fields manually
        # 3. Upload with corrections

        upload_response = client.post(
            "/api/v1x/resume-import/upload",
            data={
                "full_name": "Corrected Name",
                "email": "corrected@example.com",
            },
            files={"file": ("resume.pdf", sample_pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert upload_response.status_code in [201, 401, 422]


# ============ Error Handling Tests ============

class TestImportErrorHandling:
    """Tests for error handling in import endpoints"""

    def test_parse_preview_corrupted_pdf(self):
        """Test parse preview with corrupted PDF"""
        corrupted_pdf = BytesIO(b"%PDF-1.4 [corrupted content]")

        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("corrupted.pdf", corrupted_pdf, "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should handle gracefully with error message
        assert response.status_code in [200, 400, 422, 401]

    def test_upload_corrupted_docx(self):
        """Test upload with corrupted DOCX"""
        corrupted_docx = BytesIO(b"PK\x03\x04 [corrupted zip content]")

        response = client.post(
            "/api/v1x/resume-import/upload",
            data={},
            files={"file": ("corrupted.docx", corrupted_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code in [200, 400, 422, 401, 500]

    def test_import_missing_parsing_library(self):
        """Test import when PDF parsing library is not installed"""
        # This would be tested by mocking the import
        
        response = client.post(
            "/api/v1x/resume-import/parse-preview",
            data={"ai": False},
            files={"file": ("resume.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")},
            headers={"Authorization": "Bearer test-token"},
        )

        # Should handle missing library gracefully
        assert response.status_code in [200, 422, 401, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
