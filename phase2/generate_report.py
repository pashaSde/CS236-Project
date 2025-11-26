"""
Generate markdown findings report from analysis results

Usage:
    python generate_report.py --output-dir output
"""

import pandas as pd
import os
import argparse


def generate_findings_report(output_dir="output"):
    """
    Generate a markdown file with analysis findings by reading CSV files
    
    Args:
        output_dir (str): Base output directory containing csvs/ and report/ subdirectories
    """
    csvs_dir = os.path.join(output_dir, "csvs")
    report_dir = os.path.join(output_dir, "report")
    
    # Ensure report directory exists
    os.makedirs(report_dir, exist_ok=True)
    
    # Read CSV files
    try:
        cancel_pdf = pd.read_csv(os.path.join(csvs_dir, "cancellation_rates.csv"))
        avg_pdf = pd.read_csv(os.path.join(csvs_dir, "averages.csv"))
        bookings_pdf = pd.read_csv(os.path.join(csvs_dir, "monthly_bookings.csv"))
        season_pdf = pd.read_csv(os.path.join(csvs_dir, "seasonality.csv")).sort_values('total_revenue', ascending=False)
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find CSV files in {csvs_dir}")
        print(f"   Please run analysis.py first to generate the CSV files.")
        print(f"   Details: {e}")
        return
    
    # Get peak revenue month for seasonality answer
    peak_revenue_month = season_pdf.iloc[0]
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Create markdown content
    report = f"""# Hotel Booking Analysis

## 1. Cancellation Rates

Calculate cancellation rates for each month.

![Cancellation Rates](../plots/cancellation_rates.png)

---

## 2. Averages

Compute average price and average number of nights for each month.

![Average Price and Nights Stayed](../plots/averages.png)

---

## 3. Monthly Bookings by Market Segment

Count monthly bookings by market segment.

**Note:** In categories, TA means Travel Agents and TO means Tour Operators.

![Monthly Bookings by Market Segment](../plots/monthly_bookings.png)

---

## 4. Seasonality

Identify the most popular month of the year for bookings based on revenue.

**Most Popular Month:** {month_names[int(peak_revenue_month['arrival_month'])]} with ${peak_revenue_month['total_revenue']:,.2f} in revenue

![Seasonality Analysis](../plots/seasonality.png)

---

*Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Save report
    report_path = os.path.join(report_dir, "analysis_findings.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"✅ Findings report generated: {report_path}")
    return report_path


def main():
    """Main function to run from command line"""
    parser = argparse.ArgumentParser(
        description='Generate hotel booking analysis findings report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_report.py
  python generate_report.py --output-dir output
  python generate_report.py --output-dir ../output/phase-2
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Base output directory containing csvs/ subdirectory (default: output)'
    )
    
    args = parser.parse_args()
    
    print(f"Generating findings report from CSV files in '{args.output_dir}/csvs/'...")
    generate_findings_report(args.output_dir)


if __name__ == "__main__":
    main()
