== 0. Executive Summary
<executive-summary>
In this phase, we set up a local PySpark environment, used two CSV
datasets (`customer-reservations.csv` and `hotel-booking.csv`),
performed exploratory data analysis (EDA), and data preprocessing.

#horizontalrule

== 1. Installation Process
<installation-process>
=== 1.1 Unpack the Project
<unpack-the-project>
```bash
unzip CS236-Project.zip
cd CS236-Project
```

=== 1.2 Creating a Virtual Environment
<creating-a-virtual-environment>
```bash
python3 -m venv venv
source venv/bin/activate
```

=== 1.3 Install Dependencies
<install-dependencies>
```bash
pip install -r requirements.txt
```

=== 1.4 Installing Java 11
<installing-java-11>
```bash
brew install openjdk@11
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
```

=== 1.5 Running the Script
<running-the-script>
```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home \
&& export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH" \
&& spark-submit phase1-eda.py
```

== 2. Exploratory Data Analysis Process
<exploratory-data-analysis-process>
This sections contains EDA process and findings that we performed on the
datasets - `customer-reservations.csv` and `hotel-booking.csv`. Here we
will answer What, Why and Insights we gained from the EDA steps that we
performed.

#horizontalrule

=== 2.1 Schema Inspection
<schema-inspection>
==== Customer Reservations Schema
<customer-reservations-schema>
#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,auto,auto,),
    table.header([Column Name], [Data Type], [Nullable],),
    table.hline(),
    [Booking\_ID], [string], [True],
    [stays\_in\_weekend\_nights], [integer], [True],
    [stays\_in\_week\_nights], [integer], [True],
    [lead\_time], [integer], [True],
    [arrival\_year], [integer], [True],
    [arrival\_month], [integer], [True],
    [arrival\_date], [integer], [True],
    [market\_segment\_type], [string], [True],
    [avg\_price\_per\_room], [double], [True],
    [booking\_status], [string], [True],
  )]
  , kind: table
  )

#horizontalrule

==== Hotel Bookings Schema
<hotel-bookings-schema>
#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,auto,auto,),
    table.header([Column Name], [Data Type], [Nullable],),
    table.hline(),
    [hotel], [string], [True],
    [booking\_status], [integer], [True],
    [lead\_time], [integer], [True],
    [arrival\_year], [integer], [True],
    [arrival\_month], [string], [True],
    [arrival\_date\_week\_number], [integer], [True],
    [arrival\_date\_day\_of\_month], [integer], [True],
    [stays\_in\_weekend\_nights], [integer], [True],
    [stays\_in\_week\_nights], [integer], [True],
    [market\_segment\_type], [string], [True],
    [country], [string], [True],
    [avg\_price\_per\_room], [double], [True],
    [email], [string], [True],
  )]
  , kind: table
  )

==== Why:
<why>
We did this step to confirm proper loading of datasets using PySpark and
to get brief idea about the dataset like columns and its data types.

==== Insights:
<insights>
- #emph[Customer Reservations:] This Dataset contains columns of
  different data types. We have Numeric fields such as `lead_time`,
  `arrival_year`, and `avg_price_per_room`, and categorical fields like
  `market_segment_type` and `booking_status` were `StringType`. \
- #emph[Hotel Bookings:] This Dataset contains columns of 2 data types.
  `arrival_month` was inferred as a `StringType` (e.g., "July",
  "September"), while other date components were integers.

#horizontalrule

=== 2.2 Size Inspection
<size-inspection>
==== Why:
<why-1>
We did to check the size of the database in order to fit within Spark in
memory limits.

==== Insights:
<insights-1>
- #emph[Customer Reservations:] #strong[36,275 rows × 10 columns] ---
  each row represents one unique booking (`Booking_ID`). \
- #emph[Hotel Bookings:] #strong[78,703 rows × 13 columns] --- includes
  additional contextual fields such as `hotel`, `country`, and `email`.
  \
- Both datasets are of moderate size and fit comfortably within Spark's
  in-memory analysis limits.

=== 2.3 Missing Values
<missing-values>
==== Missing Values Count --- Customer Reservations
<missing-values-count-customer-reservations>
#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,auto,),
    table.header([Column Name], [Missing Values],),
    table.hline(),
    [Booking\_ID], [0],
    [stays\_in\_weekend\_nights], [0],
    [stays\_in\_week\_nights], [0],
    [lead\_time], [0],
    [arrival\_year], [0],
    [arrival\_month], [0],
    [arrival\_date], [0],
    [market\_segment\_type], [0],
    [avg\_price\_per\_room], [0],
    [booking\_status], [0],
  )]
  , kind: table
  )

#strong[Note:] Customer Reservations Dataset does not have
`arrival_date_week_number` field. However, during data preprocessing, we
calculate it from the existing date components (year, month, day) using
ISO 8601 week numbering to ensure compatibility with the Hotel Bookings
Dataset.

#horizontalrule

==== Missing Values Count --- Hotel Bookings
<missing-values-count-hotel-bookings>
#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,auto,),
    table.header([Column Name], [Missing Values],),
    table.hline(),
    [hotel], [0],
    [booking\_status], [0],
    [lead\_time], [0],
    [arrival\_year], [0],
    [arrival\_month], [0],
    [arrival\_date\_week\_number], [0],
    [arrival\_date\_day\_of\_month], [0],
    [stays\_in\_weekend\_nights], [0],
    [stays\_in\_week\_nights], [0],
    [market\_segment\_type], [0],
    [country], [405],
    [avg\_price\_per\_room], [0],
    [email], [0],
  )]
  , kind: table
  )

==== Why:
<why-2>
We did this step to find incomplete fields to decide whether to remove
them or to fill in mean value.

==== Insights:
<insights-2>
- #emph[Customer Reservations:] #strong[0 missing values] across all the
  columns. \
- #emph[Hotel Bookings:] Only the `country` column contained #strong[405
  missing values] all other columns were complete. \
- Overall both the datasets were almost complete with only Hotel
  Bookings Dataset having very less percentage of missing values.

#horizontalrule

=== 2.4 Distinct Values Inspection
<distinct-values-inspection>
==== Distinct Values Count --- Customer Reservations
<distinct-values-count-customer-reservations>
#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,auto,),
    table.header([Column Name], [Distinct Count],),
    table.hline(),
    [Booking\_ID], [36,275],
    [stays\_in\_weekend\_nights], [8],
    [stays\_in\_week\_nights], [18],
    [lead\_time], [352],
    [arrival\_year], [2],
    [arrival\_month], [12],
    [arrival\_date], [31],
    [market\_segment\_type], [5],
    [avg\_price\_per\_room], [3,930],
    [booking\_status], [2],
  )]
  , kind: table
  )

#horizontalrule

==== Distinct Values Count --- Hotel Bookings
<distinct-values-count-hotel-bookings>
#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,auto,),
    table.header([Column Name], [Distinct Count],),
    table.hline(),
    [hotel], [2],
    [booking\_status], [2],
    [lead\_time], [439],
    [arrival\_year], [2],
    [arrival\_month], [12],
    [arrival\_date\_week\_number], [53],
    [arrival\_date\_day\_of\_month], [31],
    [stays\_in\_weekend\_nights], [17],
    [stays\_in\_week\_nights], [32],
    [market\_segment\_type], [8],
    [country], [159],
    [avg\_price\_per\_room], [6,985],
    [email], [77,144],
  )]
  , kind: table
  )

==== Why:
<why-3>
This is essential EDA process which results in determining primary keys,
redundancy and also helps in process of prediction.

==== Insights:
<insights-3>
- #emph[Customer Reservations:]
  - `Booking_ID` had #strong[36,275 unique values], which means every
    row can be uniquely identified from the `Booking_ID` hence it can be
    used as a primary. \
  - `market_segment_type` had #strong[5 categories] and can be used to
    draw significant inference from the data. \
  - `booking_status` had #strong[2 values] --- #emph[Canceled] and
    #emph[Not\_Canceled]. \
  - No duplicate rows found. \
- #emph[Hotel Bookings:]
  - `hotel` had 2 values (#emph[City Hotel], #emph[Resort Hotel]). \
  - `market_segment_type` had 8 categories. \
  - `country` had 159 unique codes. \
  - `email` had 77,144 unique entries, nearly matching total rows,
    implying one booking per customer.

#horizontalrule

=== 2.5 Correlation Inspection
<correlation-inspection>
==== Correlation map - Customer Reservations
<correlation-map---customer-reservations>
#figure(image("./output/eda_customer_reservartions_correlation.png"),
  caption: [
    Correlation for Customer Reservation
  ]
)

==== Correlation map - Hotel Bookings
<correlation-map---hotel-bookings>
#figure(image("./output/eda_hotel_bookings_correlation.png"),
  caption: [
    Correlation for Customer Reservation
  ]
)

==== Why:
<why-4>
This steps helps us in finding strong and weak relationships between
continuous variables.

==== Insights:
<insights-4>
- #strong[Customer Reservations]
  - `stays_in_week_nights` and `stays_in_weekend_nights` show a
    #strong[moderate positive correlation (0.18)] which seems reasonable
    as customers might extend their stays for the weekend if booked
    initially for the week days.
  - `lead_time` has #strong[very weak or no correlation] with
    `avg_price_per_room` (≈ -0.06). This insight was kind of surprising
    as booking earlier had little or no effect in average room price.
  - Other relationships are near zero, confirming that most numeric
    fields (dates, lead time, price) are largely independent.
- #strong[Hotel Bookings]
  - `stays_in_week_nights` and `stays_in_weekend_nights` have a
    #strong[strong positive correlation (\~0.50)] with same reasoning as
    above.
  - `lead_time` and `booking_status` are #strong[positively correlated
    (\~0.33)] which means bookings made far in advance are slightly more
    likely to be canceled. \
  - `lead_time` and `avg_price_per_room` show a #strong[weak negative
    correlation (-0.10)] --- earlier bookings tend to be marginally
    cheaper.
  - Other variables show near-zero correlations, suggesting minimal
    temporal dependencies.

#horizontalrule

=== Summary
<summary>
Both the datasets are well structured and mostly clean. With EDA steps
performed, we were able to find some useful insights from the datasets.
These findings are useful in next steps of the data pre processing.

= Data Merge & Integration
<data-merge-integration>
== 1. Dataset Overview
<dataset-overview>
=== 1.1 Source Datasets
<source-datasets>
We merged two hotel booking datasets: - Customer reservations: 36,275
records from customer booking system (no duplicates) - Hotel bookings:
78,703 records from hotel management system (1 duplicate removed during
cleaning → 78,702 records) - Total merged: 114,977 records

== 2. Key Challenges
<key-challenges>
=== 2.1 Different Column Names for Same Data
<different-column-names-for-same-data>
#figure(
  align(center)[#table(
    columns: (46.27%, 43.28%, 10.45%),
    align: (auto,auto,auto,),
    table.header([Customer Reservations Dataset], [Hotel Bookings
      Dataset], [Issue],),
    table.hline(),
    [`Booking_ID`], [N/A], [Hotel data lacks booking identifiers],
    [`arrival_date`], [`arrival_date_day_of_month`], [Different naming
    for same field],
  )]
  , kind: table
  )

=== 2.2 Different Data Formats
<different-data-formats>
#figure(
  align(center)[#table(
    columns: (9.09%, 45.45%, 45.45%),
    align: (auto,auto,auto,),
    table.header([Field], [Customer Reservations Format], [Hotel
      Bookings Format],),
    table.hline(),
    [`booking_status`], [Text ('Canceled', 'Not\_Canceled')], [Binary
    (0, 1)],
    [`arrival_month`], [Numeric (1-12)], [Text ('January', 'February',
    …)],
  )]
  , kind: table
  )

=== 2.3 Missing Columns
<missing-columns>
#figure(
  align(center)[#table(
    columns: (24.32%, 43.24%, 32.43%),
    align: (auto,auto,auto,),
    table.header([Dataset], [Missing Columns], [Resolution],),
    table.hline(),
    [Customer Reservations], [hotel, country, email,
    arrival\_date\_week\_number], [Added (hotel, country, email as NULL;
    week\_number calculated)],
    [Hotel Bookings], [booking\_id], [Generated with INN prefix and
    offset],
  )]
  , kind: table
  )

#horizontalrule

== 3. Data Cleaning Decisions
<data-cleaning-decisions>
=== 3.1 Customer Reservations Dataset
<customer-reservations-dataset>
==== Column Standardization
<column-standardization>
- Renamed `Booking_ID` → `booking_id` for consistency
- Renamed `arrival_date` → `arrival_date_day_of_month` for clarity

==== Missing Column Handling
<missing-column-handling>
#figure(
  align(center)[#table(
    columns: (15.38%, 7.69%, 76.92%),
    align: (auto,auto,auto,),
    table.header([Column Added], [Value], [Rationale],),
    table.hline(),
    [`hotel`], [NULL], [Customer Reservations system doesn't track hotel
    type],
    [`country`], [NULL], [Geographic information not available],
    [`email`], [NULL], [Privacy/data availability limitation],
    [`arrival_date_week_number`], [Calculated], [Computed from
    arrival\_year, arrival\_month, arrival\_date\_day\_of\_month],
  )]
  , kind: table
  )

==== Week Number Calculation
<week-number-calculation>
The customer reservations dataset doesn't include week numbers, but we
can derive them from the existing date components:

```python
# Construct date from year, month, day components
date_string = concat_ws('-', year, padded_month, padded_day)
arrival_date = to_date(date_string)

# Extract ISO week number (1-53)
arrival_date_week_number = weekofyear(arrival_date)
```

==== Why:
<why-5>
- Maximizes data completeness by deriving missing information
- Uses ISO 8601 week numbering standard
- Enables consistent week-based analysis across both datasets
- Using NULL for hotel, country, and email follows database best
  practices for truly missing data

==== Duplicate Removal
<duplicate-removal>
- Checked for duplicate rows using all fields
- No duplicates found in customer reservations dataset

#horizontalrule

=== 3.2 Hotel Bookings Dataset
<hotel-bookings-dataset>
==== Booking Status Standardization
<booking-status-standardization>
- #strong[Original:] Binary (0 = not canceled, 1 = canceled)
- #strong[Target:] Text ('Not\_Canceled', 'Canceled')

```python
when(col('booking_status') == 0, 'Not_Canceled').otherwise('Canceled')
```

==== Why:
<why-6>
- Matches customer reservations dataset format
- Self-documenting (no need to remember 0/1 mapping)
- Prevents accidental numeric operations on categorical data

#horizontalrule

==== Arrival Month Conversion
<arrival-month-conversion>
- #strong[Original:] Text ('January', 'February', …, 'December')
- #strong[Target:] Numeric (1-12)

==== Why:
<why-7>
- Matches customer reservations dataset format
- Enables numeric operations (sorting, filtering, calculations)
- Reduces storage space
- Facilitates time-series analysis

#horizontalrule

==== Booking ID Generation
<booking-id-generation>
- #strong[Format:] INN50000, INN50001, INN50002, …
- #strong[Offset:] Starting at 50,000

==== Why:
<why-8>
Customer Reservations Dataset Booking IDs range from INN00001 to
INN36275. Starting hotel IDs at 50,000 prevents ID collision while
maintaining the same INN prefix pattern.

#horizontalrule

==== Duplicate Removal
<duplicate-removal-1>
- Found 1 duplicate record in Hotel Bookings Dataset
- Removed during cleaning process

#horizontalrule

=== 3.3 Final Merged Dataset Transformations
<final-merged-dataset-transformations>
==== Boolean Conversion
<boolean-conversion>
- #strong[Field:] `booking_status` → `is_canceled`
- #strong[Format:] Boolean (True/False)

==== Why:
<why-9>
- Database-ready format (PostgreSQL BOOLEAN type)
- More efficient storage (1 byte vs 12+ bytes for text)
- Enables boolean operators in queries
- Clearer semantic meaning

==== ID Simplification
<id-simplification>
- #strong[Field:] `booking_id` → `id`

==== Why:
<why-10>
Shorter, simpler column name for the primary identifier.

#horizontalrule

== 4. Schema Alignment Strategy
<schema-alignment-strategy>
=== 4.1 Unified Column Set
<unified-column-set>
The following 14 columns were standardized across both datasets:

#figure(
  align(center)[#table(
    columns: (35.14%, 29.73%, 35.14%),
    align: (auto,auto,auto,),
    table.header([Column Name], [Data Type], [Description],),
    table.hline(),
    [`booking_id`], [String], [Unique booking identifier],
    [`hotel`], [String], [Hotel type (or NULL)],
    [`booking_status`], [String], [Cancellation status],
    [`lead_time`], [Integer], [Days between booking and arrival],
    [`arrival_year`], [Integer], [Year of arrival],
    [`arrival_month`], [Integer], [Month of arrival (1-12)],
    [`arrival_date_week_number`], [Integer], [ISO week number (or
    calculated)],
    [`arrival_date_day_of_month`], [Integer], [Day of month],
    [`stays_in_weekend_nights`], [Integer], [Weekend nights booked],
    [`stays_in_week_nights`], [Integer], [Weekday nights booked],
    [`market_segment_type`], [String], [Market segment],
    [`country`], [String], [Country code (or NULL)],
    [`avg_price_per_room`], [Double], [Average room price],
    [`email`], [String], [Customer email (or NULL)],
  )]
  , kind: table
  )

#horizontalrule

== 5. Merge Methodology
<merge-methodology>
=== 5.1 Union vs Join Decision
<union-vs-join-decision>
#strong[Chosen Approach:] UNION (vertical concatenation)

```python
merged_df = customer_aligned.union(hotel_aligned)
```

==== Why:
<why-11>
- Datasets represent independent booking sources
- No natural join key exists between them
- Goal is to combine all records, not match them
- Preserves all records from both sources

#strong[Alternative Considered:] JOIN operation \
#strong[Why Rejected:] Would require matching keys and could lose
records; datasets are complementary, not overlapping.

#horizontalrule

=== 5.2 Duplicate Detection and Removal
<duplicate-detection-and-removal>
Duplicates are removed at the individual dataset level before merging: -
#strong[Customer Reservations:] Checked and found 0 duplicates -
#strong[Hotel Bookings:] Found and removed 1 duplicate record
(Lisa\_M\@gmail.com with identical booking details)

#horizontalrule

== 6. Final Schema
<final-schema>
=== 6.1 Merged Dataset Structure
<merged-dataset-structure>
#strong[Total Columns:] 14

#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,auto,auto,),
    table.header([Column], [Type], [Constraints],),
    table.hline(),
    [`id`], [String], [Primary identifier],
    [`hotel`], [String], [Nullable],
    [`is_canceled`], [Boolean], [Not null],
    [`lead_time`], [Integer], [Not null],
    [`arrival_year`], [Integer], [Not null],
    [`arrival_month`], [Integer], [Not null],
    [`arrival_date_week_number`], [Integer], [Not null],
    [`arrival_date_day_of_month`], [Integer], [Not null],
    [`stays_in_weekend_nights`], [Integer], [Not null],
    [`stays_in_week_nights`], [Integer], [Not null],
    [`market_segment_type`], [String], [Not null],
    [`country`], [String], [Nullable],
    [`avg_price_per_room`], [Double], [Not null],
    [`email`], [String], [Nullable],
  )]
  , kind: table
  )

#horizontalrule

== 7. Key Decisions Summary
<key-decisions-summary>
=== 7.1 Data Quality
<data-quality>
- #strong[NULL Representation:] Missing data stored as NULL (blank in
  CSV) rather than placeholder strings
- #strong[Duplicate Handling:] Business-logic-based deduplication
  catching semantic duplicates
- #strong[ID Strategy:] Offset-based ID generation preventing collisions
  between datasets

=== 7.2 Database Readiness
<database-readiness>
- #strong[Boolean Fields:] booking\_status converted to is\_canceled
  boolean
- #strong[Consistent Types:] All data types aligned and validated
- #strong[Primary Key:] Unique id field for every record

=== 7.3 Data Lineage
<data-lineage>
- #strong[Customer Reservation Records:] INN00001 - INN36275 (36,275
  records)
- #strong[Hotel Booking Records:] INN50000 - INN128702 (78,702 records
  after deduplication)
- #strong[Total Records:] 114,977 unique bookings

#horizontalrule

== 8. Summary
<summary-1>
The data merge process successfully unified two independent booking
systems into a single, clean dataset suitable for analysis and database
import. Key achievements include:

+ #strong[Schema Harmonization:] Resolved naming and format
  inconsistencies
+ #strong[Data Quality:] Removed duplicates and standardized missing
  data handling
+ #strong[Database Compatibility:] Converted to database-friendly
  formats (booleans, NULLs)
+ #strong[Data Integrity:] Prevented ID collisions through offset
  strategy
+ #strong[Complete Traceability:] All decisions documented with clear
  rationale

The resulting merged dataset provides a comprehensive view of hotel
bookings across both systems, ready for downstream analysis and database
integration.
