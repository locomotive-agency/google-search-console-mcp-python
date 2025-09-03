"""Tests for Google Search Console MCP Server."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from google_search_console_mcp_python.server import mcp


@pytest.fixture
def mock_credentials_path(tmp_path: Path) -> Path:
    """Create a mock credentials file."""
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text(
        json.dumps(
            {
                "type": "service_account",
                "project_id": "test-project",
                "private_key_id": "key-id",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9W8bA\n-----END PRIVATE KEY-----\n",
                "client_email": "test@test-project.iam.gserviceaccount.com",
                "client_id": "123456789",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
    )
    return creds_file


class TestGSCMCPServer:
    """Test suite for GSC MCP Server functionality."""

    @pytest.mark.asyncio
    async def test_search_analytics_tool(self):
        """Test search analytics tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.get_search_analytics = AsyncMock(
                return_value={
                    "rows": [
                        {
                            "query": "test",
                            "clicks": 100,
                            "impressions": 1000,
                            "ctr": 0.1,
                            "position": 5.0,
                        }
                    ],
                    "responseAggregationType": "auto",
                }
            )

            result = await mcp.call_tool(
                "search_analytics",
                {
                    "site_url": "https://example.com",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "dimensions": "query,page",
                },
            )

            assert "rows" in result
            assert len(result["rows"]) == 1
            assert result["rows"][0]["query"] == "test"
            assert result["rows"][0]["clicks"] == 100

    @pytest.mark.asyncio
    async def test_list_sites_tool(self):
        """Test list sites tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.list_sites = AsyncMock(
                return_value=[
                    {"siteUrl": "https://example.com", "permissionLevel": "siteOwner"}
                ]
            )

            result = await mcp.call_tool("list_sites", {})

            assert "sites" in result
            assert len(result["sites"]) == 1
            assert result["sites"][0]["siteUrl"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_get_site_tool(self):
        """Test get site tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.get_site = AsyncMock(
                return_value={
                    "siteUrl": "https://example.com",
                    "permissionLevel": "siteOwner",
                }
            )

            result = await mcp.call_tool(
                "get_site", {"site_url": "https://example.com"}
            )

            assert result["siteUrl"] == "https://example.com"
            assert result["permissionLevel"] == "siteOwner"

    @pytest.mark.asyncio
    async def test_add_site_tool(self):
        """Test add site tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.add_site = AsyncMock(
                return_value={
                    "status": "success",
                    "message": "Site https://example.com added successfully",
                }
            )

            result = await mcp.call_tool(
                "add_site", {"site_url": "https://example.com"}
            )

            assert result["status"] == "success"
            assert "added successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_site_tool(self):
        """Test delete site tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.delete_site = AsyncMock(
                return_value={
                    "status": "success",
                    "message": "Site https://example.com removed successfully",
                }
            )

            result = await mcp.call_tool(
                "delete_site", {"site_url": "https://example.com"}
            )

            assert result["status"] == "success"
            assert "removed successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_inspect_url_tool(self):
        """Test URL inspection tool functionality."""
        with patch("google_search_console_mcp_python.server.gsc_client") as mock_client:
            mock_client.inspect_url = AsyncMock(
                return_value={
                    "inspectionUrl": "https://example.com/page",
                    "siteUrl": "https://example.com",
                    "indexStatusResult": {"verdict": "PASS"},
                }
            )

            result = await mcp.call_tool(
                "inspect_url",
                {
                    "site_url": "https://example.com",
                    "inspection_url": "https://example.com/page",
                },
            )

            assert result["inspectionUrl"] == "https://example.com/page"
            assert result["indexStatusResult"]["verdict"] == "PASS"

    @pytest.mark.asyncio
    async def test_missing_credentials_error(self):
        """Test error handling when credentials are missing."""
        with patch("google_search_console_mcp_python.server.gsc_client", None):
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("list_sites", {})

            assert "not initialized" in str(exc_info.value).lower()
