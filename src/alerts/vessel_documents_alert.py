#src/alerts/vessel_documents_alert.py
"""
Vessel Documents Alert Implementation.

Monitors vessel_documents table for updates and sends notifications
to vessel-specific email addresses with company-specific CC lists.
"""
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import text
import logging

from src.core.base_alert import BaseAlert
from src.core.config import AlertConfig
from src.db_utils import get_db_connection, validate_query_file

logger = logging.getLogger(__name__)


class VesselDocumentsAlert(BaseAlert):
    """
    Alert for vessel document updates.
    
    Sends individual emails to each vessel with their updated documents,
    with appropriate CC lists based on vessel email domain.
    """

    
    def __init__(self, config: AlertConfig):
        """
        Initialize vessel documents alert.
        
        Args:
            config: AlertConfig instance
        """
        super().__init__(config)
        
        # Alert-specific configuration
        self.sql_query_file = 'NewVesselCertificates.sql'
        self.lookback_days = config.vessel_documents_lookback_days

        # Log instantiation
        self.logger.info(f"[OK] VesselDocumentsAlert instance created")

    
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch vessel documents from database.
        
        Returns:
            DataFrame with columns: vessel_id, vessel, vsl_email, document_id, document_name,
            document_category, updated_at, expiration_date, comments
        """
        # Load SQL query
        query_path = self.config.queries_dir / self.sql_query_file
        query_sql = validate_query_file(query_path)
        query = text(query_sql)
        
        # Execute query
        with get_db_connection() as conn:
            df = pd.read_sql_query(query, conn)
        
        self.logger.info(f"Fetched {len(df)} total vessel document record(s)")
        return df

    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for documents updated in the last lookback_days.
        
        Args:
            df: Raw DataFrame from database
            
        Returns:
            Filtered DataFrame with only recently updated documents
        """
        if df.empty:
            return df
        
        # Convert updated_at to timezone-aware datetime
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        
        # If the datetime is timezone-naive, localize it to UTC first, then convert to local timezone
        if df['updated_at'].dt.tz is None:
            df['updated_at'] = df['updated_at'].dt.tz_localize('UTC').dt.tz_convert(self.config.timezone)
        else:
            # If already timezone-aware, just convert to local timezone
            df['updated_at'] = df['updated_at'].dt.tz_convert(self.config.timezone)
        
        # Calculate cutoff date (timezone-aware)
        cutoff_date = datetime.now(tz=ZoneInfo(self.config.timezone)) - timedelta(days=self.lookback_days)
        
        # Filter for recent updates (now both are timezone-aware)
        df_filtered = df[df['updated_at'] >= cutoff_date].copy()
        
        # Format dates for display
        df_filtered['updated_at'] = df_filtered['updated_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format expiration_date if present
        if 'expiration_date' in df_filtered.columns:
            df_filtered['expiration_date'] = pd.to_datetime(
                df_filtered['expiration_date'], errors='coerce'
            ).dt.strftime('%Y-%m-%d')
            # Replace NaT with empty string
            df_filtered['expiration_date'] = df_filtered['expiration_date'].fillna('')
        
        self.logger.info(
            f"Filtered to {len(df_filtered)} document(s) updated in last {self.lookback_days} day(s)"
        )
        
        return df_filtered
    

    def route_notifications(self, df: pd.DataFrame) -> List[Dict]:
        """
        Route documents to vessel-specific emails with company CC lists.

        Each vessel gets a separate email with only their documents.
        CC recipients are determined by vessel email domain.

        Args:
            df: Filtered DataFrame with recent document updates

        Returns:
            List of notification job dictionaries
        """
        jobs = []

        # Group by vessel
        grouped = df.groupby(['vessel', 'vsl_email'])

        for (vessel_name, vessel_email), vessel_df in grouped:
            # Determine CC recipients based on email domain
            cc_recipients = self._get_cc_recipients(vessel_email)

            # Keep full data with tracking columns for the job
            # The formatter will handle which columns to display
            full_data = vessel_df.copy()

            # Specify WHICH cols to DISPLAY IN EMAIL *and* in WHAT ORDER here:
            display_columns = [
                    'vessel',
                    'document_name',
                    'document_category',
                    'updated_at',
                    'expiration_date',
                    'comments'
            ]

            # Create notification job
            job = {
                'recipients': [vessel_email],
                'cc_recipients': cc_recipients,
                'data': full_data,  # Keep all columns including vessel_id, document_id
                'metadata': {
                    'vessel_name': vessel_name,
                    'alert_title': 'Vessel Document Updates',
                    'company_name': self._get_company_name(vessel_email),
                    'display_columns': display_columns
                }
            }

            jobs.append(job)

            self.logger.info(
                f"Created notification job for vessel '{vessel_name}' "
                f"({len(full_data)} document(s)) -> {vessel_email} "
                f"(CC: {len(cc_recipients)})"
            )

        return jobs


    def _get_cc_recipients(self, vessel_email: str) -> List[str]:
        """
        Determine CC recipients based on vessel email domain.
        Always includes internal recipients.
        
        Args:
            vessel_email: Vessel's email address
            
        Returns:
            List of CC email addresses (domain-specific + internal)
        """
        vessel_email_lower = vessel_email.lower()
        
        # Start with empty list
        cc_list = []
        
        # Check each configured domain
        for domain, recipients_config in self.config.email_routing.items():
            if domain.lower() in vessel_email_lower:
                cc_list = recipients_config.get('cc', [])
                break
        
        # Always add internal recipients to CC list
        all_recipients = list(set(cc_list + self.config.internal_recipients))
        
        return all_recipients
    

    def _get_company_name(self, vessel_email: str) -> str:
        """
        Determine company name based on vessel email domain.
        
        Args:
            vessel_email: Vessel's email address
            
        Returns:
            Company name string
        """
        vessel_email_lower = vessel_email.lower()
        
        if 'prominence' in vessel_email_lower:
            return 'Prominence Maritime S.A.'
        elif 'seatraders' in vessel_email_lower:
            return 'Sea Traders S.A.'
        else:
            return 'Prominence Maritime S.A.'   # Default company name


    def get_tracking_key(self, row: pd.Series) -> str:
        """
        Generate tracking key from vessel ID and document ID.

        Args:
            row: DataFrame row

        Returns:
            Tracking key string in format "vessel_{vessel_id}_doc_{document_id}"
        """
        try:
            vessel_id = row['vessel_id']
            document_id = row['document_id']

            return f"vessel_{vessel_id}_doc_{document_id}"
        except KeyError as e:
            self.logger.error(f"Missing column in row for tracking key: {e}")
            self.logger.error(f"Available columns: {list(row.index)}")
            raise


    def get_subject_line(self, data: pd.DataFrame, metadata: Dict) -> str:
        """
        Generate email subject line.
        
        Args:
            data: DataFrame for this notification
            metadata: Metadata including vessel_name
            
        Returns:
            Email subject string
        """
        vessel_name = metadata.get('vessel_name', 'Vessel')
        doc_count = len(data)
        
        return f"AlertDev | {vessel_name.upper()} | {doc_count} Vessel Document Update{'' if doc_count==1 else 's'}"

    
    def get_required_columns(self) -> List[str]:
        """
        Return required columns for this alert.
        
        Returns:
            List of required column names
        """
        return [
            'vessel_id',
            'document_id',
            'vessel',
            'vsl_email',
            'document_name',
            'document_category',
            'updated_at'
        ]
