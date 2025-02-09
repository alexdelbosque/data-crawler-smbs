# Crawling and Scraping for Market Research

## Overview
This repository documents the technical process of crawling and scraping data from online sources to analyze market trends, business software usage, and customer behavior. The methodology includes data extraction, automated browsing, and software identification.

## Table of Contents
- [Data Collection Process](#data-collection-process)
  - [Crawling Business Data with Octoparse](#1-crawling-business-data-with-octoparse)
  - [Identifying Online Booking Systems](#2-identifying-online-booking-systems)
  - [Advanced Software Identification](#3-advanced-software-identification)
- [Data Cleaning & Storage](#data-cleaning--storage)
- [Data Analysis & Insights](#data-analysis--insights)
- [Scraping Additional Data for AI Applications](#scraping-additional-data-for-ai-applications)
- [Broader Industry Applications](#broader-industry-applications)

## Data Collection Process

### 1. Crawling Business Data with Octoparse
- Extract business information from Google Maps, including:
  - **Business name**
  - **Address**
  - **Website**
  - **Ratings and reviews**
- Crawl all reviews associated with each business.
- Estimate customer volume and revenue using:
  - **Average ticket size**
  - **Customer-review ratio** (typically 5-10%)

### 2. Identifying Online Booking Systems
- Use **Cursor** and **Selenium** to:
  - Visit business websites.
  - Search for booking-related text ("Book Now," "Schedule Appointment," etc.).
  - Extract booking page links.
- Analyze extracted URLs to identify subdomain patterns indicating software providers (e.g., `appname.booking.clinicname.com`).

### 3. Advanced Software Identification
- Clean and filter extracted URLs.
- Identify and count recurring booking software providers.
- Visit booking pages without an identifiable subdomain to analyze source code for software-related keywords.
- Match businesses to their booking software providers.

## Data Cleaning & Storage
- To store and process data efficiently, create the following SQL tables:
  - **clinics_usa** – Stores business information from Google Maps.
  - **clinics_usa_reviews** – Stores customer reviews, ratings, and review dates.
  - **software** – Stores identified booking software providers and their usage statistics.
  - **website_scraping** – Stores results from website scraping, including booking button detection.
- **Review Date Conversion:**
  - Google Maps provides review timestamps in text format (e.g., "9 months ago" or "2 years ago").
  - Convert these timestamps into a standard date format using the data import timestamp.
  - Example logic:
    - If the current date is `2024-02-01` and a review says "2 years ago," it is converted to `2022-02-01`.
    - If a review says "9 months ago," it is converted to `2023-05-01`.

## Data Analysis & Insights
- **SQL tables** store extracted data for easy querying and visualization.
- Key statistics generated include:
  - Most-used **booking software** in the market.
  - Relationship between **revenue and software usage**.
  - Age of businesses using different booking systems (estimated from earliest review dates).
- Findings provide insights into:
  - Market penetration of specific software.
  - Technology adoption trends.

## Scraping Additional Data for AI Applications
- Extract **treatment catalogs** from businesses with publicly available data (treatment name, description, price, duration, etc.).
- Structure scraped data into a formatted **knowledge base** for AI applications.
- Automate data refinement using **pre-tested prompts**.

## Broader Industry Applications
This methodology is applicable across various industries for competitive analysis and automation, including:

- **Car Dealerships** – Identifying dealerships with online booking for test drives or service appointments.
- **Dentists** – Analyzing clinic booking systems and patient volume.
- **Hospitals** – Evaluating appointment scheduling and patient management software.
- **Restaurants** – Detecting online reservation systems and food delivery platform usage (e.g., Uber Eats, OpenTable).

This approach enables efficient **data-driven decision-making** and market analysis through automation and AI integration.

---
### 🚀 Contributions
Feel free to contribute by submitting **issues** or **pull requests** to improve this documentation.

### 🛠 Technologies Used
- **Octoparse**
- **Selenium**
- **Python**
- **SQL**
