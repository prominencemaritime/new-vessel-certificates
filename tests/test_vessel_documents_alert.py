# tests/test_vessel_documents_alert.py
"""
Tests for VesselDocumentsAlert logic.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


def test_alert_initializes_correctly(mock_config):
    """Test that alert initializes with correct configuration."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    alert = VesselDocumentsAlert(mock_config)
    
    assert alert.sql_query_file == 'NewVesselCertificates.sql'
    assert alert.lookback_days == mock_config.vessel_documents_lookback_days


def test_alert_filters_data_by_lookback_days(mock_config, sample_dataframe):
    """Test that filter_data correctly filters by lookback days."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    alert = VesselDocumentsAlert(mock_config)
    alert.lookback_days = 1  # Last 24 hours
    
    # All sample data is within last 24 hours
    filtered = alert.filter_data(sample_dataframe)
    
    assert len(filtered) == 4  # All records


def test_alert_filters_out_old_data(mock_config, sample_dataframe):
    """Test that old data is filtered out."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    # Create old record by copying a row and modifying it
    old_record = sample_dataframe.iloc[[0]].copy()
    old_record['vessel_id'] = 999
    old_record['vessel'] = 'OLD VESSEL'
    old_record['vsl_email'] = 'old@test.com'
    old_record['document_id'] = 999
    old_record['document_name'] = 'Old Doc'
    old_record['updated_at'] = datetime.now() - timedelta(days=5)
    old_record['expiration_date'] = pd.NaT  # or None, but pd.NaT is cleaner
    
    df_with_old = pd.concat([sample_dataframe, old_record], ignore_index=True)
    
    alert = VesselDocumentsAlert(mock_config)
    alert.lookback_days = 1
    
    filtered = alert.filter_data(df_with_old)
    
    # Should exclude the old record
    assert len(filtered) == 4
    assert 999 not in filtered['document_id'].values


def test_alert_routes_by_vessel(mock_config, sample_dataframe):
    """Test that notifications are routed correctly by vessel."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # DEBUG: Print what we actually have
    print("\n=== DEBUG ===")
    print(f"Number of jobs: {len(jobs)}")
    for job in jobs:
        print(f"Vessel: {job['metadata']['vessel_name']}")
    print("=============\n")

    # Should create 3 jobs (TEST VESSEL 1 with 2 docs, TEST VESSEL 2 with 1, TEST VESSEL 3 with 1)
    assert len(jobs) == 3

    # Check TEST VESSEL 1 job
    vessel1_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 1')
    assert len(vessel1_job['data']) == 2
    assert vessel1_job['recipients'] == ['vessel1@vsl.company1.test']


def test_alert_assigns_correct_cc_recipients(mock_config, sample_dataframe):
    """Test that CC recipients are assigned based on email domain plus internal recipients."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    for job in jobs:
        cc_recipients = job['cc_recipients']

        # Should include ALL 4 domain-specific CC recipients (filter is OFF)
        assert 'technical@company1.test' in cc_recipients  # Changed
        assert 'operations@company1.test' in cc_recipients  # Changed
        assert 'safety@company1.test' in cc_recipients  # Changed
        assert 'marine@company1.test' in cc_recipients  # Changed

        # Should ALSO include internal recipients
        assert 'internal@test.com' in cc_recipients

        # Total: 4 domain + 1 internal = 5 recipients
        assert len(cc_recipients) == 5


def test_alert_filters_cc_by_department_when_enabled(mock_config, sample_dataframe):
    """Test that CC recipients are filtered by department when filter is enabled."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    # Enable department filtering
    mock_config.department_specific_cc_recipients_filter = True

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # Check TEST VESSEL 1 job (has Technical + HSSQE departments)
    vessel1_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 1')
    cc_recipients = vessel1_job['cc_recipients']

    # Should include ONLY Technical and Safety (HSSQE) department emails
    assert 'technical@company1.test' in cc_recipients
    assert 'safety@company1.test' in cc_recipients

    # Should NOT include Operations or Marine (no docs from those departments)
    assert 'operations@company1.test' not in cc_recipients
    assert 'marine@company1.test' not in cc_recipients

    # Should include internal recipients
    assert 'internal@test.com' in cc_recipients

    # Total: 2 department + 1 internal = 3 recipients
    assert len(cc_recipients) == 3

    # Check TEST VESSEL 2 job (only Technical department)
    vessel2_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 2')
    cc_recipients = vessel2_job['cc_recipients']

    # Should include ONLY Technical
    assert 'technical@company1.test' in cc_recipients
    assert 'operations@company1.test' not in cc_recipients
    assert 'safety@company1.test' not in cc_recipients
    assert 'marine@company1.test' not in cc_recipients

    # Should include internal recipients
    assert 'internal@test.com' in cc_recipients

    # Total: 1 department + 1 internal = 2 recipients
    assert len(cc_recipients) == 2


def test_alert_generates_correct_subject_lines(mock_config, sample_dataframe):
    """Test subject line generation."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    alert = VesselDocumentsAlert(mock_config)
    
    # Single record
    single_df = sample_dataframe.iloc[:1]
    subject_single = alert.get_subject_line(single_df, {'vessel_name': 'TEST VESSEL'})
    assert subject_single == "AlertDev | TEST VESSEL | 1 Vessel Document Update"
    
    # Multiple records
    multi_df = sample_dataframe.iloc[:3]
    subject_multi = alert.get_subject_line(multi_df, {'vessel_name': 'TEST VESSEL'})
    assert subject_multi == "AlertDev | TEST VESSEL | 3 Vessel Document Updates"


def test_alert_generates_correct_tracking_keys(mock_config, sample_dataframe):
    """Test that tracking keys are generated correctly."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    alert = VesselDocumentsAlert(mock_config)
    
    row = sample_dataframe.iloc[0]
    key = alert.get_tracking_key(row)
    
    assert key == f"vessel_{row['vessel_id']}_doc_{row['document_id']}"


def test_alert_required_columns_validation(mock_config):
    """Test that required columns are correctly defined."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    alert = VesselDocumentsAlert(mock_config)
    required = alert.get_required_columns()

    assert 'vessel_id' in required
    assert 'document_id' in required
    assert 'vessel' in required
    assert 'vsl_email' in required
    assert 'document_name' in required
    assert 'department_id' in required  # NEW
    assert 'department_name' in required  # NEW


def test_alert_validates_dataframe_columns(mock_config, sample_dataframe):
    """Test that DataFrame validation works correctly."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    
    alert = VesselDocumentsAlert(mock_config)
    
    # Should not raise exception with valid DataFrame
    alert.validate_required_columns(sample_dataframe)
    
    # Should raise exception with missing column
    invalid_df = sample_dataframe.drop(columns=['vessel_id'])
    with pytest.raises(ValueError, match="Missing required columns"):
        alert.validate_required_columns(invalid_df)


def test_alert_includes_internal_recipients_in_cc(mock_config, sample_dataframe):
    """Test that internal recipients are always included in CC."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    # Set up internal recipients
    mock_config.internal_recipients = ['admin@company.com', 'manager@company.com']

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # Check all jobs include internal recipients in CC
    for job in jobs:
        cc_recipients = job['cc_recipients']

        # Internal recipients should ALWAYS be in the CC list
        assert 'admin@company.com' in cc_recipients, \
            f"Internal recipient 'admin@company.com' missing from CC: {cc_recipients}"
        assert 'manager@company.com' in cc_recipients, \
            f"Internal recipient 'manager@company.com' missing from CC: {cc_recipients}"

        # Domain-specific recipients should also be present
        # (all sample vessels are @company1.test, filter is OFF so all 4 departments)
        assert 'technical@company1.test' in cc_recipients
        assert 'operations@company1.test' in cc_recipients
        assert 'safety@company1.test' in cc_recipients
        assert 'marine@company1.test' in cc_recipients

        # Should have 6 total CC recipients (4 domain + 2 internal)
        assert len(cc_recipients) == 6


def test_alert_internal_recipients_when_no_domain_match(mock_config):
    """Test that internal recipients are used when domain doesn't match routing."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert
    import pandas as pd
    from datetime import datetime

    # Create dataframe with unknown domain
    unknown_domain_df = pd.DataFrame({
        'vessel_id': [999],
        'vessel': ['UNKNOWN VESSEL'],
        'vsl_email': ['unknown@unknowndomain.com'],  # Not in routing
        'department_id': [1],  # ADD THIS
        'department_name': ['Technical'],  # ADD THIS
        'document_id': [999],
        'document_name': ['Test Doc'],
        'document_category': ['Safety'],
        'updated_at': [datetime.now()],
        'expiration_date': [None],
        'comments': ['']
    })

    # Set up internal recipients
    mock_config.internal_recipients = ['admin@company.com', 'manager@company.com']

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(unknown_domain_df)

    # Should have one job
    assert len(jobs) == 1

    # Should ONLY have internal recipients (no domain match)
    cc_recipients = jobs[0]['cc_recipients']
    assert 'admin@company.com' in cc_recipients
    assert 'manager@company.com' in cc_recipients
    assert len(cc_recipients) == 2  # Only internal, no domain-specific


def test_alert_deduplicates_cc_recipients(mock_config, sample_dataframe):
    """Test that duplicate emails in CC list are removed."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    # Set internal recipients to overlap with domain CC
    mock_config.internal_recipients = ['technical@prominencemaritime.com', 'admin@company.com']

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # Check that duplicates are removed
    for job in jobs:
        cc_recipients = job['cc_recipients']

        # Should not have duplicates
        assert len(cc_recipients) == len(set(cc_recipients)), \
            f"Duplicate emails found in CC list: {cc_recipients}"

        # technical@prominencemaritime.com should appear only once
        assert cc_recipients.count('technical@prominencemaritime.com') == 1


def test_alert_includes_departments_in_metadata(mock_config, sample_dataframe):
    """Test that unique departments are included in job metadata."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # Check TEST VESSEL 1 job (has 2 departments: Technical and HSSQE)
    vessel1_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 1')
    departments = vessel1_job['metadata']['departments']

    assert 'Technical' in departments
    assert 'HSSQE' in departments
    assert len(departments) == 2

    # Check TEST VESSEL 2 job (has 1 department: Technical)
    vessel2_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 2')
    departments = vessel2_job['metadata']['departments']

    assert 'Technical' in departments
    assert len(departments) == 1

    # Check TEST VESSEL 3 job (has 1 department: Operations)
    vessel3_job = next(j for j in jobs if j['metadata']['vessel_name'] == 'TEST VESSEL 3')
    departments = vessel3_job['metadata']['departments']

    assert 'Operations' in departments
    assert len(departments) == 1


def test_alert_includes_department_in_display_columns(mock_config, sample_dataframe):
    """Test that department_name is included in display columns."""
    from src.alerts.vessel_documents_alert import VesselDocumentsAlert

    alert = VesselDocumentsAlert(mock_config)
    jobs = alert.route_notifications(sample_dataframe)

    # Check that display_columns includes department_name
    for job in jobs:
        display_columns = job['metadata']['display_columns']
        
        assert 'department_name' in display_columns
        # Should be first column
        assert display_columns[0] == 'department_name'
