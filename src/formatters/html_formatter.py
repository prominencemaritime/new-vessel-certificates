#src/formatters/html_formatter.py
"""
HTML email formatter with rich styling and company branding.

Generates professional HTML emails optimized for all email clients
including Outlook, Gmail, Apple Mail, and web-based clients.
"""
from typing import Dict, Optional
import pandas as pd
from datetime import datetime
import logging
import base64

logger = logging.getLogger(__name__)


class HTMLFormatter:
    """
    Generates HTML email content with company branding.
    Uses inline styles and table-based layout for maximum compatibility.
    """

    def format(
        self,
        df: pd.DataFrame,
        run_time: datetime,
        config: 'AlertConfig',
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Generate HTML email content from DataFrame.

        Args:
            df: DataFrame with data to display
            run_time: Timestamp of this alert run
            config: AlertConfig instance for accessing settings
            metadata: Optional metadata (e.g., vessel_name, alert_title)

        Returns:
            HTML string for email body
        """
        if metadata is None:
            metadata = {}

        # Extract metadata with defaults
        alert_title = metadata.get('alert_title', 'Alert Notification')
        vessel_name = metadata.get('vessel_name', '')
        company_name = metadata.get('company_name', 'Company')

        # Determine which logos are available
        logos_html = self._build_logos_html(config)

        # Build the HTML using table-based layout with inline styles
        html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{alert_title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9fafc;">
    <!-- Outer wrapper table -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9fafc;">
        <tr>
            <td align="center" style="padding: 20px 0;">

                <!-- Main container table -->
                <table border="0" cellpadding="0" cellspacing="0" width="900" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); max-width: 900px;">

                    <!-- Header -->
                    <tr>
                        <td style="background-color: #0B4877; padding: 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="left" valign="middle" style="padding-right: 20px;">
                                        {logos_html}
                                    </td>
                                    <td align="right" valign="middle">
                                        <h1 style="margin: 0; padding: 0; color: #ffffff; font-size: 24px; font-weight: 600;">{alert_title}</h1>
                                        {f'<p style="margin: 5px 0 0 0; padding: 0; color: #d7e7f5; font-size: 14px;">{vessel_name}</p>' if vessel_name else ''}
                                        <p style="margin: 5px 0 0 0; padding: 0; color: #d7e7f5; font-size: 14px;">{run_time.strftime('%A, %d %B %Y • %H:%M %Z')}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
"""

        if df.empty:
            html += """
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding: 40px; color: #666666; font-size: 16px;">
                                        <p style="margin: 0;"><strong>No records found for the current query.</strong></p>
                                    </td>
                                </tr>
                            </table>
"""
        else:
            # Add metadata section
            html += f"""
                            <!-- Metadata box -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f8fb; border-radius: 8px; border-left: 4px solid #2EA9DE; margin-bottom: 25px;">
                                <tr>
                                    <td style="padding: 15px; font-size: 14px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="padding: 4px 0;">
                                                    <span style="font-weight: 600; color: #0B4877; display: inline-block; min-width: 140px;">Records Found:</span>
                                                    <span style="display: inline-block; background-color: #2EA9DE; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 600;">{len(df)}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 4px 0;">
                                                    <span style="font-weight: 600; color: #0B4877; display: inline-block; min-width: 140px;">Generated:</span>
                                                    <span style="color: #333333;">{run_time.strftime('%A, %B %d, %Y at %H:%M %Z')}</span>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
"""

            # Determine which columns to display
            display_columns = metadata.get('display_columns', list(df.columns))
            # Filter to only columns that exist in the dataframe
            display_columns = [col for col in display_columns if col in df.columns]

            # Build data table with inline styles
            html += """
                            <!-- Data table -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse; margin: 20px 0; font-size: 14px;">
                                <thead>
                                    <tr>
"""
            # Add column headers
            for col in display_columns:
                display_name = col.replace('_', ' ').title()
                html += f"""                                        <th style="background-color: #0B4877; color: #ffffff; text-align: left; padding: 12px; font-weight: 600; border: 1px solid #0B4877;">{display_name}</th>\n"""

            html += """                                    </tr>
                                </thead>
                                <tbody>
"""

            # Add data rows with alternating colors
            for idx, row in df.iterrows():
                row_bg = '#ffffff' if idx % 2 == 0 else '#f5f8fb'
                html += f"""                                    <tr style="background-color: {row_bg};">\n"""

                for col in display_columns:
                    value = row[col]
                    # Format None/NaN as empty string
                    if pd.isna(value):
                        display_value = ""
                    else:
                        display_value = str(value)

                    # Check if this is the vessel_id column and we should make it a link
                    if col == 'document_name' and config.enable_document_links and 'vessel_id' in row and config.base_url:
                        vessel_id = row['vessel_id']
                        doc_url = f"{config.base_url}/vessels/{vessel_id}/documents"
                        display_value = f'<a href="{doc_url}" style="color: #2EA9DE; text-decoration: none;">{display_value}</a>'

                    html += f"""                                        <td style="padding: 10px 12px; border-bottom: 1px solid #e0e6ed; color: #333333;">{display_value}</td>\n"""

                html += """                                    </tr>\n"""

            html += """                                </tbody>
                            </table>
"""

        # Footer
        html += f"""
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="font-size: 12px; color: #888888; text-align: center; padding: 20px; border-top: 1px solid #eeeeee; background-color: #f9fafc;">
                            <p style="margin: 5px 0;">This is an automated notification from {company_name}.</p>
                            <p style="margin: 5px 0;">If you have questions, please contact your system administrator.</p>
                        </td>
                    </tr>

                </table>
                <!-- End main container -->

            </td>
        </tr>
    </table>
    <!-- End outer wrapper -->
</body>
</html>
"""

        return html

    def _build_logos_html(self, config: 'AlertConfig') -> str:
        """
        Build HTML for company logos based on which are available.
        Uses inline styles for maximum compatibility.

        Args:
            config: AlertConfig instance

        Returns:
            HTML string with img tags for available logos
        """
        logos = []

        for company_name, logo_path in config.company_logos.items():
            if logo_path.exists():
                # CID format matches what EmailSender uses
                cid = f"{company_name}_logo"
                logos.append(f'<img src="cid:{cid}" alt="{company_name} logo" style="max-height: 50px; vertical-align: middle; margin-right: 15px; display: inline-block;" />')

        return '\n                                        '.join(logos)
