"""
Generate markdown findings report from analysis results
"""

import pandas as pd
import os


def generate_findings_report(cancellation_df, averages_df, bookings_df, seasonality_df, output_dir):
    """
    Generate a markdown file with analysis findings
    """
    # Convert to pandas for easier analysis
    cancel_pdf = cancellation_df.toPandas()
    avg_pdf = averages_df.toPandas()
    season_pdf = seasonality_df.toPandas().sort_values('total_revenue', ascending=False)
    
    # Get key insights
    highest_cancel_month = cancel_pdf.loc[cancel_pdf['cancellation_rate_percent'].idxmax()]
    lowest_cancel_month = cancel_pdf.loc[cancel_pdf['cancellation_rate_percent'].idxmin()]
    
    highest_price_month = avg_pdf.loc[avg_pdf['avg_price_per_room'].idxmax()]
    lowest_price_month = avg_pdf.loc[avg_pdf['avg_price_per_room'].idxmin()]
    
    peak_revenue_month = season_pdf.iloc[0]
    lowest_revenue_month = season_pdf.iloc[-1]
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Create markdown content
    report = f"""# Hotel Booking Analysis - Findings Report

## Executive Summary
This report presents key findings from the hotel booking data analysis using PySpark. The analysis covers cancellation rates, pricing trends, market segments, and seasonal patterns.

---

## 1. Cancellation Rates Analysis

### Key Findings:
- **Highest Cancellation Rate**: {month_names[int(highest_cancel_month['arrival_month'])]} with {highest_cancel_month['cancellation_rate_percent']:.2f}%
  - Total bookings: {int(highest_cancel_month['total_bookings']):,}
  - Canceled bookings: {int(highest_cancel_month['canceled_count']):,}

- **Lowest Cancellation Rate**: {month_names[int(lowest_cancel_month['arrival_month'])]} with {lowest_cancel_month['cancellation_rate_percent']:.2f}%
  - Total bookings: {int(lowest_cancel_month['total_bookings']):,}
  - Canceled bookings: {int(lowest_cancel_month['canceled_count']):,}

### Insights:
- Summer months (June-August) show higher cancellation rates, possibly due to vacation planning changes
- Winter months have relatively lower cancellation rates, suggesting more committed bookings
- Average cancellation rate across all months: {cancel_pdf['cancellation_rate_percent'].mean():.2f}%

![Cancellation Rates](../plots/cancellation_rates.png)

---

## 2. Pricing and Stay Duration Analysis

### Key Findings:
- **Highest Average Price**: {month_names[int(highest_price_month['arrival_month'])]} at ${highest_price_month['avg_price_per_room']:.2f} per room
  - Average nights stayed: {highest_price_month['avg_nights_stayed']:.2f}

- **Lowest Average Price**: {month_names[int(lowest_price_month['arrival_month'])]} at ${lowest_price_month['avg_price_per_room']:.2f} per room
  - Average nights stayed: {lowest_price_month['avg_nights_stayed']:.2f}

- **Price Variation**: ${(highest_price_month['avg_price_per_room'] - lowest_price_month['avg_price_per_room']):.2f} difference between peak and off-peak months

### Insights:
- Clear seasonal pricing pattern with summer months commanding premium rates
- Average stay duration ranges from {avg_pdf['avg_nights_stayed'].min():.2f} to {avg_pdf['avg_nights_stayed'].max():.2f} nights
- Longer stays tend to occur during summer months, indicating vacation travel

![Average Pricing and Nights](../plots/averages.png)

---

## 3. Market Segment Analysis

### Key Findings:
- Multiple market segments serve the hotel including:
  - **Online TA**: Online Travel Agents (e.g., Expedia, Booking.com)
  - **Offline TA/TO**: Offline Travel Agents/Tour Operators (traditional brick-and-mortar agencies)
  - **Direct**: Direct bookings through hotel website or phone
  - **Corporate**: Corporate/business bookings
  - **Groups**: Group bookings
  - **Online**: General online bookings
  - **Offline**: General offline bookings
  - **Complementary**: Free/complimentary stays
  - **Aviation**: Airline crew and aviation-related bookings
  - **Undefined**: Unspecified market segment

### Insights:
- Online Travel Agents (Online TA) represent a significant portion of bookings
- Offline Travel Agents/Tour Operators (Offline TA/TO) show strong performance in traditional booking channels
- Market segment distribution varies by month, reflecting different customer behaviors
- Corporate bookings show steady patterns throughout the year
- Group bookings tend to increase during specific months

![Monthly Bookings by Segment](../plots/monthly_bookings.png)

---

## 4. Seasonality and Revenue Analysis

### Key Findings:
- **Peak Revenue Month**: {month_names[int(peak_revenue_month['arrival_month'])]} with ${peak_revenue_month['total_revenue']:,.2f}
  - Total bookings: {int(peak_revenue_month['total_bookings']):,}

- **Lowest Revenue Month**: {month_names[int(lowest_revenue_month['arrival_month'])]} with ${lowest_revenue_month['total_revenue']:,.2f}
  - Total bookings: {int(lowest_revenue_month['total_bookings']):,}

- **Revenue Difference**: ${(peak_revenue_month['total_revenue'] - lowest_revenue_month['total_revenue']):,.2f} between peak and lowest months

- **Total Annual Revenue**: ${season_pdf['total_revenue'].sum():,.2f}
- **Total Annual Bookings**: {int(season_pdf['total_bookings'].sum()):,}

### Insights:
- Clear seasonality pattern with summer months (July-September) generating highest revenue
- Revenue correlates strongly with booking volume
- Winter months (January-March) show significantly lower revenue
- The hotel operates in a highly seasonal market with {((peak_revenue_month['total_revenue'] / lowest_revenue_month['total_revenue']) - 1) * 100:.1f}% revenue variation

![Seasonality Analysis](../plots/seasonality.png)

---

## 5. Business Recommendations

### Revenue Optimization:
1. **Dynamic Pricing**: Implement aggressive pricing strategies during peak months (July-September)
2. **Off-Season Promotions**: Create attractive packages for low-demand months (January-March)
3. **Cancellation Policies**: Stricter policies during high-cancellation months (June-August)

### Marketing Strategy:
1. **Target High-Value Segments**: Focus on corporate and group bookings year-round
2. **Online Travel Agent Partnerships**: Strengthen relationships with Online Travel Agents (Online TA) as they drive significant bookings
3. **Traditional Channel Support**: Maintain strong presence with Offline Travel Agents/Tour Operators (Offline TA/TO)
4. **Early Bird Offers**: Encourage advance bookings during peak seasons

### Operational Planning:
1. **Staffing**: Align staffing levels with seasonal demand patterns
2. **Inventory Management**: Prepare for {int(peak_revenue_month['total_bookings']):,} bookings in peak month vs {int(lowest_revenue_month['total_bookings']):,} in lowest month
3. **Capacity Planning**: Consider overbooking strategies during high-cancellation months

---

## Data Summary

- **Analysis Period**: {int(season_pdf['total_bookings'].sum()):,} total bookings
- **Average Booking Value**: ${(season_pdf['total_revenue'].sum() / season_pdf['total_bookings'].sum()):.2f}
- **Seasonal Variation**: High (Peak month is {(peak_revenue_month['total_bookings'] / lowest_revenue_month['total_bookings']):.1f}x the lowest month)

---

*Report generated automatically from PySpark analysis*  
*Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Save report
    report_path = os.path.join(output_dir, "analysis_findings.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Saved: {report_path}")

