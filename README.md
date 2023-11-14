# UOCIS322 - Project 5 #

### Author: Justin Noah

### Contact: jnoah@uoregon.edu

### Description

This project is an ACP Brevet time calculator. This webapp uses flask for the backend and bootstrap and jquery for the front end. To calculate the brevet start and close times, each segment / control section is used to calculate the slowest and fastest speeds given said segment. Then the distance is divided by said speed for a time adjustment, which is added to the start time. These values are requested via ajax calls and updated accordingly. MongoDB is used for storage and recall of the latest worksheet.

### Setup and Usage Instructions

Run:
```docker compose up```

Use:
Open ```http://localhost:5000``` in your favorite browser

