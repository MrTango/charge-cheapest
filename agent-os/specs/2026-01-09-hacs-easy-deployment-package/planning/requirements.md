# HACS Easy Deployment Package - Raw Requirements

**Feature Name:** HACS Easy Deployment Package

**Raw Idea/Requirements:**
Create a user-friendly deployment package for the Tibber Battery Charging blueprint that minimizes manual setup for intermediate Home Assistant users.

## Goals

1. HACS-compatible repository structure for distribution
2. Package YAML that auto-creates all helpers on restart (no manual YAML editing)
3. Entity configuration via input_text helpers (users enter sensor IDs in UI, not in YAML)
4. Comprehensive Lovelace dashboard with:
   - Overview: Status, gauges, price chart, controls
   - Statistics: Savings, history graphs, charging stats
   - Configuration: Entity setup section, solar settings, system info
5. Template sensors for dashboard data
6. Minimal user setup steps (8 steps, mostly one-click)

## Key Design Decisions

- Entity IDs configured via input_text helpers, templates use states(states('input_text.xxx')) pattern
- Dashboard includes Configuration view for first-time entity setup
- ApexCharts dependency for price charts (with fallback)
- Package creates: input_number, input_boolean, input_select, input_datetime, input_text, template sensors, binary sensors, utility meters

## Date Initiated
2026-01-09
