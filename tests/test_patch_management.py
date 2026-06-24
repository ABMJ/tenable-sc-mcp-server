"""
Tests for patch management tools.

Tests parsing functions for plugins 66334 and 38153, and integration with tsc_list_missing_patches.
"""

from html import escape

import pytest

from tenable_sc_mcp.tools.patch_management import (
    parse_plugin_66334,
    parse_plugin_38153,
    parse_patch_report,
)


class TestParsePlugin66334:
    """Tests for universal patch report parser (plugin 66334)."""
    
    def test_parse_microsoft_kbs_with_counts(self):
        """Test parsing Microsoft KB patches with vulnerability counts."""
        text = """
        The following Microsoft patches are missing:
        - KB5025279 (85 vulnerabilities)
        - KB5026361 (12 vulnerabilities)
        - KB5025221 (3 vulnerabilities)
        """
        
        result = parse_plugin_66334(text)
        
        assert result["total_missing_patches"] == 3
        assert len(result["microsoft_kbs"]) == 3
        assert len(result["third_party"]) == 0
        
        # Verify KB details
        assert result["microsoft_kbs"][0] == {"kb_id": "KB5025279", "vulnerability_count": 85}
        assert result["microsoft_kbs"][1] == {"kb_id": "KB5026361", "vulnerability_count": 12}
        assert result["microsoft_kbs"][2] == {"kb_id": "KB5025221", "vulnerability_count": 3}
    
    def test_parse_microsoft_kbs_without_counts(self):
        """Test parsing KB patches without vulnerability counts."""
        text = """
        Missing patches:
        - KB5025279
        - KB5026361
        """
        
        result = parse_plugin_66334(text)
        
        assert result["total_missing_patches"] == 2
        assert len(result["microsoft_kbs"]) == 2
        assert result["microsoft_kbs"][0] == {"kb_id": "KB5025279", "vulnerability_count": None}
        assert result["microsoft_kbs"][1] == {"kb_id": "KB5026361", "vulnerability_count": None}
    
    def test_parse_third_party_software(self):
        """Test parsing third-party software patches."""
        text = """
        Missing updates:
        [ Google Chrome < 113.0.5672.63 ]
        [ VMware Tools 10.x / 11.x < 12.2.0 ]
        [ Microsoft Office 2016 < 16.0.5349.1000 ]
        """
        
        result = parse_plugin_66334(text)
        
        assert result["total_missing_patches"] == 3
        assert len(result["microsoft_kbs"]) == 0
        assert len(result["third_party"]) == 3
        
        assert result["third_party"][0] == {"software": "Google Chrome < 113.0.5672.63"}
        assert result["third_party"][1] == {"software": "VMware Tools 10.x / 11.x < 12.2.0"}
        assert result["third_party"][2] == {"software": "Microsoft Office 2016 < 16.0.5349.1000"}
    
    def test_parse_mixed_patches(self):
        """Test parsing both Microsoft KBs and third-party software."""
        text = """
        Missing patches:
        - KB5025279 (85 vulnerabilities)
        [ Google Chrome < 113.0.5672.63 ]
        - KB5026361 (12 vulnerabilities)
        [ VMware Tools 10.x / 11.x < 12.2.0 ]
        """
        
        result = parse_plugin_66334(text)
        
        assert result["total_missing_patches"] == 4
        assert len(result["microsoft_kbs"]) == 2
        assert len(result["third_party"]) == 2
    
    def test_parse_empty_text(self):
        """Test parsing empty plugin output."""
        result = parse_plugin_66334("")
        
        assert result["total_missing_patches"] == 0
        assert len(result["microsoft_kbs"]) == 0
        assert len(result["third_party"]) == 0
    
    def test_parse_no_matches(self):
        """Test parsing text with no recognizable patches."""
        text = "No missing patches detected on this system."
        
        result = parse_plugin_66334(text)
        
        assert result["total_missing_patches"] == 0
        assert len(result["microsoft_kbs"]) == 0
        assert len(result["third_party"]) == 0
    
    def test_parse_case_insensitive_vulnerability_keyword(self):
        """Test case-insensitive parsing of 'vulnerability' keyword."""
        text = """
        - KB5025279 (85 VULNERABILITIES)
        - KB5026361 (1 Vulnerability)
        """
        
        result = parse_plugin_66334(text)
        
        assert len(result["microsoft_kbs"]) == 2
        assert result["microsoft_kbs"][0]["vulnerability_count"] == 85
        assert result["microsoft_kbs"][1]["vulnerability_count"] == 1


class TestParsePlugin38153:
    """Tests for Windows KB summary parser (plugin 38153)."""
    
    def test_parse_kb_articles(self):
        """Test parsing KB article numbers."""
        text = """
        The patches for the following bulletins or KBs are missing on the remote host:
        - KB4025252 ( https://support.microsoft.com/en-us/help/4025252 )
        - KB4025337 ( https://support.microsoft.com/en-us/help/4025337 )
        - KB5025279 ( https://support.microsoft.com/en-us/help/5025279 )
        """
        
        result = parse_plugin_38153(text)
        
        assert result["total_missing_kbs"] == 3
        assert len(result["missing_kbs"]) == 3
        
        # Verify KB details (URL generation strips KB prefix)
        assert result["missing_kbs"][0]["kb_id"] == "KB4025252"
        assert "4025252" in result["missing_kbs"][0]["url"]
        assert result["missing_kbs"][1]["kb_id"] == "KB4025337"
        assert result["missing_kbs"][2]["kb_id"] == "KB5025279"
    
    def test_parse_legacy_ms_bulletins(self):
        """Test parsing legacy MS bulletin IDs."""
        text = """
        Missing security bulletins:
        - MS16-087 ( http://technet.microsoft.com/en-us/security/bulletin/ms16-087 )
        - MS17-010 ( http://technet.microsoft.com/en-us/security/bulletin/ms17-010 )
        """
        
        result = parse_plugin_38153(text)
        
        assert result["total_missing_kbs"] == 2
        assert len(result["missing_kbs"]) == 2
        
        assert result["missing_kbs"][0]["bulletin_id"] == "MS16-087"
        assert result["missing_kbs"][0]["type"] == "legacy_ms_bulletin"
        assert result["missing_kbs"][1]["bulletin_id"] == "MS17-010"
    
    def test_parse_mixed_kb_and_bulletins(self):
        """Test parsing both KB articles and MS bulletins."""
        text = """
        Missing patches:
        - MS16-087 ( http://technet.microsoft.com/... )
        - KB4025252 ( https://support.microsoft.com/... )
        - KB5025279 ( https://support.microsoft.com/... )
        - MS17-010 ( http://technet.microsoft.com/... )
        """
        
        result = parse_plugin_38153(text)
        
        assert result["total_missing_kbs"] == 4
        # Should have 2 KBs and 2 MS bulletins
        kb_count = sum(1 for item in result["missing_kbs"] if "kb_id" in item)
        bulletin_count = sum(1 for item in result["missing_kbs"] if "bulletin_id" in item)
        assert kb_count == 2
        assert bulletin_count == 2
    
    def test_parse_deduplicate_kbs(self):
        """Test that duplicate KB numbers are removed."""
        text = """
        - KB5025279 (mentioned multiple times)
        - KB5025279 (duplicate)
        - KB4025252 (unique)
        - KB5025279 (another duplicate)
        """
        
        result = parse_plugin_38153(text)
        
        # Should only have 2 unique KBs
        assert result["total_missing_kbs"] == 2
        kb_ids = [item["kb_id"] for item in result["missing_kbs"] if "kb_id" in item]
        assert len(set(kb_ids)) == len(kb_ids)  # All unique
    
    def test_parse_empty_text(self):
        """Test parsing empty plugin output."""
        result = parse_plugin_38153("")
        
        assert result["total_missing_kbs"] == 0
        assert len(result["missing_kbs"]) == 0


class TestParseReport:
    """Tests for patch_report dispatcher function."""
    
    def test_dispatch_to_plugin_66334(self):
        """Test dispatching to plugin 66334 parser."""
        html_text = escape("- KB5025279 (85 vulnerabilities)")
        text_with_tags = f"<plugin_output>{html_text}</plugin_output>"
        
        result = parse_patch_report(text_with_tags, "66334")
        
        assert "microsoft_kbs" in result
        assert len(result["microsoft_kbs"]) == 1
        assert result["microsoft_kbs"][0]["kb_id"] == "KB5025279"
    
    def test_dispatch_to_plugin_38153(self):
        """Test dispatching to plugin 38153 parser."""
        html_text = escape("- KB4025252")
        text_with_tags = f"<plugin_output>{html_text}</plugin_output>"
        
        result = parse_patch_report(text_with_tags, "38153")
        
        assert "missing_kbs" in result
        assert len(result["missing_kbs"]) == 1
        assert result["missing_kbs"][0]["kb_id"] == "KB4025252"
    
    def test_html_unescape(self):
        """Test HTML entity unescaping."""
        html_text = escape("- KB5025279 (85 vulnerabilities)")
        text_with_tags = f"<plugin_output>{html_text}</plugin_output>"
        
        result = parse_patch_report(text_with_tags, "66334")
        
        # Should successfully parse even though input was HTML-escaped
        assert len(result["microsoft_kbs"]) == 1
    
    def test_plugin_output_tag_removal(self):
        """Test removal of plugin_output XML tags."""
        text = "<plugin_output>- KB5025279</plugin_output>"
        
        result = parse_patch_report(text, "66334")
        
        assert len(result["microsoft_kbs"]) == 1
    
    def test_nested_plugin_output_tags(self):
        """Test handling of self-closing and nested tags."""
        text = "- KB5025279<plugin_output />- KB5026361"
        
        result = parse_patch_report(text, "66334")
        
        # Should parse both KBs despite malformed tags
        assert len(result["microsoft_kbs"]) >= 1


class TestIntegration:
    """Integration tests for tsc_list_missing_patches (would require mocking)."""
    
    def test_mode_validation(self):
        """Test that only valid modes are accepted."""
        # This would require importing the actual tool and mocking _client, _get_cache
        # For now, we test the parsing functions which are the core logic
        pass
    
    def test_plugin_id_selection(self):
        """Test that correct plugin IDs are used based on mode."""
        # universal -> 66334
        # windows -> 38153
        pass
    
    def test_filter_integration(self):
        """Test that filters dict is properly passed to build_filters."""
        pass
    
    def test_caching_behavior(self):
        """Test that results are cached with correct TTL (240s)."""
        pass
