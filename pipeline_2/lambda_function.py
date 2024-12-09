from report_generator import get_previous_day, get_redshift_connection, set_schema, gather_report_data, generate_html_report
from typing import Dict


def lambda_handler(event: dict, context: dict) -> Dict[str, str]:
    prev_day = get_previous_day()
    conn = get_redshift_connection()
    cursor = conn.cursor()

    set_schema(cursor)
    report_data = gather_report_data(cursor, prev_day)
    html_content = generate_html_report(report_data, prev_day)

    cursor.close()
    conn.close()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html_content
    }
