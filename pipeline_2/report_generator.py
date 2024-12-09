import os
import json
from datetime import datetime, timedelta
from psycopg2.extensions import cursor
from load import get_redshift_connection


def get_previous_day() -> str:
    """Get the date for the previous day."""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def set_schema(cursor: cursor) -> None:
    """Set the search path to the specific schema."""
    cursor.execute("SET search_path TO ellie_bradley_schema;")


def get_total_transaction_value_all_trucks(cursor: cursor, previous_day: str) -> float:
    """Retrieve the total transaction value across all trucks."""
    cursor.execute("""
        SELECT SUM(total) AS total_transaction_value_all_trucks
        FROM FACT_Transaction
        WHERE DATE(at) = %s
    """, (previous_day,))
    return cursor.fetchone()[0]


def get_truck_data_summary(cursor: cursor, previous_day: str) -> list:
    """Retrieve summary data for each truck, ordered by total transaction value."""
    cursor.execute("""
        SELECT truck_id, SUM(total) AS total_revenue, AVG(total) AS average_transaction_value,
               COUNT(*) AS transaction_count
        FROM FACT_Transaction
        WHERE DATE(at) = %s
        GROUP BY truck_id
        ORDER BY total_revenue DESC
    """, (previous_day,))
    return cursor.fetchall()


def get_transaction_count_per_truck(cursor: cursor, previous_day: str) -> list:
    """Retrieve transaction count per truck, ordered from highest to lowest."""
    cursor.execute("""
        SELECT truck_id, COUNT(*) AS transaction_count
        FROM FACT_Transaction
        WHERE DATE(at) = %s
        GROUP BY truck_id
        ORDER BY transaction_count DESC
    """, (previous_day,))
    return cursor.fetchall()


def get_average_transaction_value_per_truck(cursor: cursor, previous_day: str) -> list:
    """Retrieve average transaction value per truck, ordered from highest to lowest."""
    cursor.execute("""
        SELECT truck_id, AVG(total) AS average_transaction_value
        FROM FACT_Transaction
        WHERE DATE(at) = %s
        GROUP BY truck_id
        ORDER BY average_transaction_value DESC
    """, (previous_day,))
    return cursor.fetchall()


def get_average_total_transaction_value(cursor: cursor, previous_day: str) -> float:
    """Retrieve the average transaction value across all trucks."""
    cursor.execute("""
        SELECT AVG(total) AS average_total_transaction_value
        FROM FACT_Transaction
        WHERE DATE(at) = %s
    """, (previous_day,))
    return cursor.fetchone()[0]


def gather_report_data(cursor: cursor, previous_day: str) -> dict:
    """Gather all report data by calling individual data retrieval functions."""
    return {
        "total_transaction_value_all_trucks": get_total_transaction_value_all_trucks(cursor, previous_day),
        "truck_data_summary": get_truck_data_summary(cursor, previous_day),
        "transaction_count_per_truck": get_transaction_count_per_truck(cursor, previous_day),
        "average_transaction_value_per_truck": get_average_transaction_value_per_truck(cursor, previous_day),
        "average_total_transaction_value": get_average_total_transaction_value(cursor, previous_day)
    }


def generate_report_json(data: dict, prev_day: str) -> dict:
    """Generate and save the report as a JSON file in the report_data folder."""
    return {
        "date": prev_day,
        "total_transaction_value_all_trucks": data["total_transaction_value_all_trucks"],
        "average_total_transaction_value": data["average_total_transaction_value"],
        "truck_data_summary": [
            {
                "truck_id": truck_id,
                "total_revenue": total_revenue,
                "average_transaction_value": average_transaction_value,
                "transaction_count": transaction_count
            } for truck_id, total_revenue, average_transaction_value, transaction_count in data["truck_data_summary"]
        ],
        "transaction_count_per_truck": [
            {"truck_id": truck_id, "transaction_count": transaction_count}
            for truck_id, transaction_count in data["transaction_count_per_truck"]
        ],
        "average_transaction_value_per_truck": [
            {"truck_id": truck_id, "average_transaction_value": average_transaction_value}
            for truck_id, average_transaction_value in data["average_transaction_value_per_truck"]
        ]
    }


def generate_html_report(data: dict, previous_day: str) -> str:
    """Generate a html file containing a simple report of key metrics. """
    html_content = f"""
    <html>
    <head>
        <title>Daily Truck Transactions Report for {previous_day}</title>
    </head>
    <body>
        <h2>Daily Truck Transactions Report for {previous_day}</h2>
        <p><strong>Total Transaction Value across all trucks:</strong> £{data["total_transaction_value_all_trucks"]}</p>
        <p><strong>Average Total Transaction Value:</strong> £{data["average_total_transaction_value"]:.2f}</p>

        <h3>Truck Data Summary</h3>
        <table>
            <tr><th>Truck ID</th><th>Total Revenue (£)</th><th>Average Transaction Value (£)</th><th>Transaction Count</th></tr>
            {"".join(f"<tr><td>{truck_id}</td><td>{total_revenue}</td><td>{average_transaction_value:.2f}</td><td>{transaction_count}</td></tr>" for truck_id, total_revenue, average_transaction_value, transaction_count in data["truck_data_summary"])}
        </table>

        <h3>Transaction Count per Truck</h3>
        <table>
            <tr><th>Truck ID</th><th>Transaction Count</th></tr>
            {"".join(f"<tr><td>{truck_id}</td><td>{transaction_count}</td></tr>" for truck_id, transaction_count in data["transaction_count_per_truck"])}
        </table>

        <h3>Average Transaction Value per Truck</h3>
        <table>
            <tr><th>Truck ID</th><th>Average Transaction Value (£)</th></tr>
            {"".join(f"<tr><td>{truck_id}</td><td>{average_transaction_value:.2f}</td></tr>" for truck_id,
                     average_transaction_value in data["average_transaction_value_per_truck"])}
        </table>
    </body>
    </html>
    """
    return html_content


def save_to_file(data: dict, folder_name: str, filename: str) -> None:
    """Save the report data to a JSON file in the specified folder."""
    os.makedirs(folder_name, exist_ok=True)
    filepath = os.path.join(folder_name, filename)
    with open(filepath, "w") as f:
        if isinstance(data, dict):
            json.dump(data, f, indent=4)
        else:
            f.write(data)
    print(f"Report saved to {filepath}")


def generate_report() -> None:
    """Main function to connect to the database, retrieve data, and generate the report."""
    prev_day = get_previous_day()
    conn = get_redshift_connection()
    cursor = conn.cursor()

    set_schema(cursor)
    report_data = gather_report_data(cursor, prev_day)

    json_data = generate_report_json(report_data, prev_day)
    save_to_file(json_data, folder_name="report_data",
                 filename=f"report_data_{prev_day}.json")

    html_content = generate_html_report(report_data, prev_day)
    save_to_file(html_content, folder_name="report_data",
                 filename=f"report_data_{prev_day}.html")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    generate_report()
