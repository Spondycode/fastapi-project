from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import io
import uuid
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI!"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_read_all_items():
    """Test getting all items."""
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


class TestUploadToImageKit:
    """Test cases for upload_to_imagekit function."""

    @patch('app.images.imagekit')
    @pytest.mark.asyncio
    async def test_upload_to_imagekit_success(self, mock_imagekit):
        """Test that upload_to_imagekit successfully uploads a file and returns the correct URL."""
        from app.images import upload_to_imagekit
        from fastapi import UploadFile
        
        # Create a mock upload result
        mock_upload_result = MagicMock()
        mock_upload_result.url = "https://ik.imagekit.io/demo/test-file.jpg"
        mock_upload_result.file_id = "test-file-id"
        mock_upload_result.name = "test.jpg"
        
        # Configure the mock imagekit client
        mock_imagekit.upload_file.return_value = mock_upload_result
        
        # Create a test file
        file_content = b"fake image content"
        test_file = UploadFile(
            filename="test.jpg",
            file=io.BytesIO(file_content)
        )
        
        # Call the function
        result = await upload_to_imagekit(test_file)
        
        # Assertions
        assert result.url == "https://ik.imagekit.io/demo/test-file.jpg"
        assert result.file_id == "test-file-id"
        assert result.name == "test.jpg"
        assert mock_imagekit.upload_file.called


class TestUploadFileEndpoint:
    """Test cases for the /upload endpoint."""

    @patch('app.main.upload_to_imagekit')
    def test_upload_file_stores_imagekit_url(self, mock_upload_to_imagekit):
        """Test that upload_file endpoint correctly uses upload_to_imagekit and stores the ImageKit URL."""
        # Create a mock upload result
        mock_upload_result = MagicMock()
        mock_upload_result.url = "https://ik.imagekit.io/demo/uploaded-file.jpg"
        mock_upload_to_imagekit.return_value = mock_upload_result
        
        # Prepare test file data
        file_content = b"test image data"
        files = {
            "file": ("test-image.jpg", io.BytesIO(file_content), "image/jpeg")
        }
        data = {
            "caption": "Test caption for image"
        }
        
        # Make the request
        response = client.post("/upload", files=files, data=data)
        
        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["url"] == "https://ik.imagekit.io/demo/uploaded-file.jpg"
        assert response_data["filename"] == "test-image.jpg"
        assert response_data["file_type"] == "image/jpeg"
        assert response_data["caption"] == "Test caption for image"
        assert "id" in response_data
        assert "created_at" in response_data
        
        # Verify upload_to_imagekit was called
        assert mock_upload_to_imagekit.called

    @patch('app.main.upload_to_imagekit')
    def test_upload_file_without_caption(self, mock_upload_to_imagekit):
        """Test uploading a file without a caption."""
        # Create a mock upload result
        mock_upload_result = MagicMock()
        mock_upload_result.url = "https://ik.imagekit.io/demo/no-caption.png"
        mock_upload_to_imagekit.return_value = mock_upload_result
        
        # Prepare test file data without caption
        file_content = b"test image data"
        files = {
            "file": ("no-caption.png", io.BytesIO(file_content), "image/png")
        }
        
        # Make the request
        response = client.post("/upload", files=files)
        
        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["caption"] is None
        assert response_data["url"] == "https://ik.imagekit.io/demo/no-caption.png"


class TestDeleteItemEndpoint:
    """Test cases for the DELETE /items/{item_id} endpoint."""

    @patch('app.main.upload_to_imagekit')
    def test_delete_item_success(self, mock_upload_to_imagekit):
        """Test that delete_item successfully deletes an existing post by ID."""
        # First, create a post to delete
        mock_upload_result = MagicMock()
        mock_upload_result.url = "https://ik.imagekit.io/demo/to-delete.jpg"
        mock_upload_to_imagekit.return_value = mock_upload_result
        
        file_content = b"test image"
        files = {"file": ("delete-me.jpg", io.BytesIO(file_content), "image/jpeg")}
        
        create_response = client.post("/upload", files=files)
        assert create_response.status_code == 200
        created_post = create_response.json()
        post_id = created_post["id"]
        
        # Now delete the post
        delete_response = client.delete(f"/items/{post_id}")
        
        # Assertions
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["message"] == "Post deleted successfully"
        assert delete_data["id"] == post_id
        
        # Verify the post is actually deleted
        get_response = client.get(f"/items/{post_id}")
        assert get_response.status_code == 404

    def test_delete_item_invalid_uuid(self):
        """Test that delete_item returns a 400 error for an invalid UUID format."""
        invalid_ids = [
            "not-a-uuid",
            "12345",
            "invalid-format-abc",
            "123e4567-e89b-12d3",  # incomplete UUID
            "123e4567-e89b-12d3-a456-42661417400g",  # invalid character 'g'
        ]
        
        for invalid_id in invalid_ids:
            response = client.delete(f"/items/{invalid_id}")
            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid UUID format"

    def test_delete_item_not_found(self):
        """Test that delete_item returns a 404 error if the post ID does not exist."""
        # Generate a random UUID that doesn't exist in the database
        non_existent_id = str(uuid.uuid4())
        
        response = client.delete(f"/items/{non_existent_id}")
        
        # Assertions
        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

    def test_delete_item_multiple_times(self):
        """Test that attempting to delete an already deleted post returns 404."""
        with patch('app.main.upload_to_imagekit') as mock_upload:
            # Create a post
            mock_upload_result = MagicMock()
            mock_upload_result.url = "https://ik.imagekit.io/demo/double-delete.jpg"
            mock_upload.return_value = mock_upload_result
            
            file_content = b"test"
            files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}
            create_response = client.post("/upload", files=files)
            post_id = create_response.json()["id"]
            
            # First deletion should succeed
            first_delete = client.delete(f"/items/{post_id}")
            assert first_delete.status_code == 200
            
            # Second deletion should fail with 404
            second_delete = client.delete(f"/items/{post_id}")
            assert second_delete.status_code == 404
            assert second_delete.json()["detail"] == "Post not found"
