### 7 Amazon QuickSight (Dashboarding)

Amazon QuickSight is used to visualise telemetry data stored in Amazon S3 and queried through Athena.

The QuickSight dashboard uses SPICE for improved performance and scheduled refresh, providing near-real-time analytics while reducing query overhead on Athena.

---

### Dashboard Capabilities

The dashboard provides near-real-time insights into sensor readings, including:

* Temperature trends  
* Carbon monoxide (CO) levels  
* Sound intensity  
* Light levels  

Key features include:

* Time-series visualisations for sensor metrics  
* A recent readings table displaying the latest telemetry values  
* Aggregated views to identify trends and anomalies  

---

### Data Integration

QuickSight queries data via Athena, which reads structured JSON data stored in Amazon S3. This enables scalable and cost-effective analytics over large datasets without impacting the operational DynamoDB workload.

---

## Data Query Workflow

Telemetry data stored in Amazon S3 is queried using Amazon Athena and transformed into an analytics-ready dataset for QuickSight.

### Query Logic

The Athena query performs the following transformations:

- Converts ISO 8601 timestamp strings into a proper datetime format
- Extracts a human-readable 24-hour time format for display
- Filters recent data for efficient dashboard performance

```sql
SELECT
  device_id,
  timestamp,
  date_parse(timestamp, '%Y-%m-%dT%H:%i:%sZ') AS ts,
  date_format(date_parse(timestamp, '%Y-%m-%dT%H:%i:%sZ'), '%H:%i') AS time_24h,
  temperature_c,
  co_ppm_est,
  sound_raw,
  light_raw
FROM indusstream.telemetry_analytics
WHERE date_parse(timestamp, '%Y-%m-%dT%H:%i:%sZ') >= current_timestamp - interval '2' day
ORDER BY ts DESC;
```
### Data Freshness

Due to the architecture (S3 → Athena → QuickSight), the dashboard operates in near-real-time rather than real-time.

Data freshness depends on:

* S3 data ingestion timing  
* Athena query execution  
* SPICE dataset refresh schedules  

---

### Dashboard Overview

The dashboard demonstrates how telemetry data flows from edge devices into a cloud-native analytics stack, enabling monitoring, alerting, and historical analysis.

![QuickSight Dashboard](../tests/quicksight-dashboard.png)