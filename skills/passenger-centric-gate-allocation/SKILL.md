---
name: passenger-centric-gate-allocation
description: Optimize departure gate assignments for transit aircraft by prioritizing passenger location over aircraft convenience. Use this skill when determining gate locations for arriving or transit aircraft at airports with multiple concourses, especially when a significant portion of passengers are transferring between flights.
---

# Passenger-Centric Gate Allocation Strategy

## When to Use
- Determining departure gate locations for arriving or transit aircraft
- Managing airport operations with multiple concourses
- Reducing passenger stress and connection delays for transfer passengers
- Evaluating gate assignment policies that prioritize aircraft convenience

## Prerequisites
- Airport with multiple concourses
- Transit passenger flow data
- Available gates (not zero availability)

## Procedure

### 1. Analyze Passenger Location
Identify where the majority of transit passengers are currently located in the terminal (e.g., after arriving from a specific flight or concourse).

### 2. Evaluate Current Assignment Logic
Determine if the current gate assignment is based on:
- Proximity to hangar
- Where the plane arrived
- Domestic route origins
- Other aircraft convenience factors

### 3. Apply Passenger-Centric Override
Assign the departure gate to the location closest to the passengers, regardless of:
- Where the plane is currently parked
- Where the plane was serviced
- Traditional aircraft convenience preferences

### 4. Execute Aircraft Towing
If the aircraft is not at the passenger-convenient gate:
- Arrange for aircraft towing from current concourse to passenger-required concourse
- Coordinate with ground handling teams

### 5. Operational Reality Check
Acknowledge the operational principle:
- Aircraft do not experience stress from being towed a few hundred yards
- Passengers experience significant stress from rushing between concourses
- Prioritize human experience over mechanical convenience

### 6. Measure Success
Track the following metrics:
- Percentage of transit passengers forced to change concourses
- Connection delays caused by waiting for transferring passengers
- Target: Reduce concourse changes (e.g., from two-thirds to one-third)

## Constraints
- Does not apply if gate availability is zero
- Must not compromise safety regulations
- Requires coordination with ground handling for aircraft towing

## Key Variables
- **passenger_location**: The specific concourse or area where transit passengers are currently located
- **plane_convenience_location**: The gate nearest the hangar or arrival point preferred by ground handlers
- **transit_ratio**: The fraction of passengers required to change concourses