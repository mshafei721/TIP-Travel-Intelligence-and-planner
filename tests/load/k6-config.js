/**
 * TIP - Travel Intelligence & Planner
 * k6 Load Test Configuration
 *
 * Target: p95 < 300ms at 100 VUs
 *
 * Installation:
 *   - Windows: choco install k6 OR winget install k6
 *   - macOS: brew install k6
 *   - Linux: sudo apt install k6
 *
 * Usage:
 *   k6 run tests/load/k6-config.js
 *   k6 run tests/load/k6-config.js --vus 100 --duration 5m
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthLatency = new Trend('health_latency');
const tripsLatency = new Trend('trips_latency');
const profileLatency = new Trend('profile_latency');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'https://tip-travel-intelligence-and-planner-production.up.railway.app';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || ''; // Set via environment for authenticated tests

// Test options
export const options = {
  // Stages for ramping up/down
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 VUs
    { duration: '1m', target: 50 },    // Ramp up to 50 VUs
    { duration: '2m', target: 100 },   // Ramp up to 100 VUs
    { duration: '2m', target: 100 },   // Stay at 100 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],

  // Thresholds - fail if these are not met
  thresholds: {
    http_req_duration: ['p(95)<300'], // p95 must be < 300ms
    errors: ['rate<0.01'],             // Error rate < 1%
    health_latency: ['p(95)<100'],     // Health check p95 < 100ms
    trips_latency: ['p(95)<300'],      // Trips API p95 < 300ms
    profile_latency: ['p(95)<300'],    // Profile API p95 < 300ms
  },
};

// Helper function for authenticated requests
function authHeaders() {
  if (AUTH_TOKEN) {
    return {
      'Authorization': `Bearer ${AUTH_TOKEN}`,
      'Content-Type': 'application/json',
    };
  }
  return {
    'Content-Type': 'application/json',
  };
}

// Default function - main test scenario
export default function () {
  // ==========================================
  // Scenario 1: Health Check (Public)
  // ==========================================
  group('Health Check', function () {
    const startTime = Date.now();
    const res = http.get(`${BASE_URL}/api/health`);
    healthLatency.add(Date.now() - startTime);

    const passed = check(res, {
      'health status is 200': (r) => r.status === 200,
      'health response has status field': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.status === 'healthy';
        } catch {
          return false;
        }
      },
    });

    errorRate.add(!passed);
  });

  sleep(0.5);

  // ==========================================
  // Scenario 2: Trips List (Authenticated)
  // ==========================================
  if (AUTH_TOKEN) {
    group('Trips API', function () {
      const startTime = Date.now();
      const res = http.get(`${BASE_URL}/api/trips`, {
        headers: authHeaders(),
      });
      tripsLatency.add(Date.now() - startTime);

      const passed = check(res, {
        'trips status is 200': (r) => r.status === 200,
        'trips response is array': (r) => {
          try {
            const body = JSON.parse(r.body);
            return Array.isArray(body) || (body.trips && Array.isArray(body.trips));
          } catch {
            return false;
          }
        },
      });

      errorRate.add(!passed);
    });

    sleep(0.5);

    // ==========================================
    // Scenario 3: Profile (Authenticated)
    // ==========================================
    group('Profile API', function () {
      const startTime = Date.now();
      const res = http.get(`${BASE_URL}/api/profile`, {
        headers: authHeaders(),
      });
      profileLatency.add(Date.now() - startTime);

      const passed = check(res, {
        'profile status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      });

      errorRate.add(!passed);
    });

    sleep(0.5);
  }

  // Random think time between iterations
  sleep(Math.random() * 2 + 1);
}

// Setup function - runs once before test
export function setup() {
  console.log(`Starting load test against: ${BASE_URL}`);
  console.log(`Auth token provided: ${AUTH_TOKEN ? 'Yes' : 'No'}`);

  // Verify connectivity
  const res = http.get(`${BASE_URL}/api/health`);
  if (res.status !== 200) {
    throw new Error(`Cannot connect to ${BASE_URL}. Health check returned ${res.status}`);
  }

  return {
    startTime: new Date().toISOString(),
  };
}

// Teardown function - runs once after test
export function teardown(data) {
  console.log(`Load test completed. Started at: ${data.startTime}`);
}

// Handle test summary
export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    duration: data.state.testRunDurationMs,
    vus_max: data.metrics.vus_max ? data.metrics.vus_max.values.max : 0,
    http_reqs: data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0,
    http_req_duration_p95: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'] : 0,
    errors: data.metrics.errors ? data.metrics.errors.values.rate : 0,
    passed: Object.values(data.root_group.checks).every(c => c.passes === c.passes + c.fails),
  };

  console.log('\n=== Load Test Summary ===');
  console.log(`Duration: ${(summary.duration / 1000 / 60).toFixed(2)} minutes`);
  console.log(`Max VUs: ${summary.vus_max}`);
  console.log(`Total Requests: ${summary.http_reqs}`);
  console.log(`p95 Latency: ${summary.http_req_duration_p95.toFixed(2)}ms`);
  console.log(`Error Rate: ${(summary.errors * 100).toFixed(2)}%`);
  console.log(`Result: ${summary.http_req_duration_p95 < 300 ? 'PASS' : 'FAIL'}`);

  return {
    'stdout': JSON.stringify(summary, null, 2),
    'tests/load/results.json': JSON.stringify(summary, null, 2),
  };
}
