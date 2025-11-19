# tests/test_formatters.py
"""
Tests for HTML and text email formatters.
"""
import pytest
from datetime import datetime
from src.formatters.html_formatter import HTMLFormatter
from src.formatters.text_formatter import TextFormatter


def test_html_formatter_generates_valid_html(mock_config, sample_dataframe):
    """Test that HTML formatter generates valid HTML."""
    formatter = HTMLFormatter()
    run_time = datetime.now()

    metadata = {
        'alert_title': 'Test Alert',
        'vessel_name': 'TEST VESSEL',
        'company_name': 'Test Company',
        'display_columns': ['document_name', 'document_category', 'updated_at']
    }

    html = formatter.format(sample_dataframe, run_time, mock_config, metadata)

    assert '<!DOCTYPE html' in html
    assert 'Test Alert' in html
    assert 'TEST VESSEL' in html
    assert 'Certificate A' in html


def test_html_formatter_handles_empty_dataframe(mock_config):
    """Test that HTML formatter handles empty DataFrame gracefully."""
    formatter = HTMLFormatter()
    run_time = datetime.now()

    import pandas as pd
    empty_df = pd.DataFrame()

    metadata = {'alert_title': 'Test Alert', 'vessel_name': 'TEST'}

    html = formatter.format(empty_df, run_time, mock_config, metadata)

    assert 'No records found' in html


def test_html_formatter_displays_only_specified_columns(mock_config, sample_dataframe):
    """Test that only specified columns are displayed."""
    formatter = HTMLFormatter()
    run_time = datetime.now()

    metadata = {
        'alert_title': 'Test',
        'display_columns': ['document_name', 'document_category']  # Only these
    }

    html = formatter.format(sample_dataframe, run_time, mock_config, metadata)

    # Should include specified columns
    assert 'Document Name' in html
    assert 'Document Category' in html

    # Should NOT include other columns
    assert 'Expiration Date' not in html or 'expiration_date' not in html.lower()


'''
def test_html_formatter_creates_links_when_enabled(mock_config, sample_dataframe):
    """Test that document links are created when enabled."""
    formatter = HTMLFormatter()
    run_time = datetime.now()

    mock_config.enable_document_links = True
    mock_config.base_url = 'https://test.com'

    metadata = {
        'alert_title': 'Test',
        'display_columns': ['document_name']
    }

    html = formatter.format(sample_dataframe, run_time, mock_config, metadata)

    assert 'href=' in html
    assert 'https://test.com/vessels' in html


def test_html_formatter_no_links_when_disabled(mock_config, sample_dataframe):
    """Test that no links are created when disabled."""
    formatter = HTMLFormatter()
    run_time = datetime.now()

    mock_config.enable_document_links = False

    metadata = {
        'alert_title': 'Test',
        'display_columns': ['document_name']
    }

    html = formatter.format(sample_dataframe, run_time, mock_config, metadata)

    # Should contain document name but not as link
    assert 'Certificate A' in html
    # href should only be in general page structure, not for documents
    assert html.count('href=') < 2  # Minimal hrefs, none for documents
'''


def test_text_formatter_generates_plain_text(mock_config, sample_dataframe):
    """Test that text formatter generates plain text."""
    formatter = TextFormatter()
    run_time = datetime.now()

    metadata = {
        'alert_title': 'Test Alert',
        'vessel_name': 'TEST VESSEL',
        'display_columns': ['document_name', 'document_category']
    }

    text = formatter.format(sample_dataframe, run_time, mock_config, metadata)

    assert 'Test Alert' in text
    assert 'TEST VESSEL' in text
    assert 'Certificate A' in text
    assert '<' not in text  # No HTML tags


def test_text_formatter_handles_empty_dataframe(mock_config):
    """Test that text formatter handles empty DataFrame."""
    formatter = TextFormatter()
    run_time = datetime.now()

    import pandas as pd
    empty_df = pd.DataFrame()

    metadata = {'alert_title': 'Test', 'vessel_name': 'TEST'}

    text = formatter.format(empty_df, run_time, mock_config, metadata)

    assert 'No records' in text or 'no records' in text.lower()
