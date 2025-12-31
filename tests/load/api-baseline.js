/**
 * TIP - API Performance Baseline Tests
 *
 * Performance targets from master-plan.md:
 * - /api/health: p95 < 100ms
 * - /api/trips (GET): p95 < 500ms
 * - /api/trips (POST): p95 < 2000ms
 *
 * Usage:
 *   k6 run tests/load/api-baseline.js
 *   k6 run tests/load/api-baseline.js --env BASE_URL=http://localhost:8000
 *   k6 run tests/load/api-baseline.js --env AUTH_TOKEN=your_jwt_token
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthLatency = new Trend('health_latency', true);
const tripsGetLatency = new Trend('trips_get_latency', true);
const tripsPostLatency = new Trend('trips_post_latency', true);
const requestCount = new Counter('request_count');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

// Test options - baseline performance test
export const options = {
  scenarios: {
    // Scenario 1: Health check baseline (high load, should handle well)
    health_baseline: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      exec: 'healthCheck',
      tags: { scenario: 'health' },
    },
    // Scenario 2: Trips GET baseline (moderate load)
    trips_get_baseline: {
      executor: 'constant-vus',
      vus: 5,
      duration: '60s',
      startTime: '30s',
      exec: 'tripsGet',
      tags: { scenario: 'trips_get' },
    },
    // Scenario 3: Trips POST baseline (light load - expensive operation)
    trips_post_baseline: {
      executor: 'constant-arrival-rate',
      rate: 1, // 1 request per second
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 2,
      maxVUs: 5,
      startTime: '90s',
      exec: 'tripsPost',
      tags: { scenario: 'trips_post' },
    },
  },

  // Thresholds from master-plan.md
  thresholds: {
    'health_latency{scenario:health}': ['p(95)<100'],        // p95 < 100ms
    'trips_get_latency{scenario:trips_get}': ['p(95)<500'],  // p95 < 500ms
    'trips_post_latency{scenario:trips_post}': ['p(95)<2000'], // p95 < 2000ms
    errors: ['rate<0.01'], // Error rate < 1%
  },
};

// Helper for authenticated requests
function authHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

// Scenario 1: Health Check
export function healthCheck() {
  const startTime = Date.now();
  const res = http.get(`${BASE_URL}/api/health`);
  healthLatency.add(Date.now() - startTime);
  requestCount.add(1);

  const passed = check(res, {
    'health status is 200': (r) => r.status === 200,
    'health response is valid': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'healthy' || body.status === 'ok';
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!passed);
  sleep(0.1);
}

// Scenario 2: Trips GET
export function tripsGet() {
  if (!AUTH_TOKEN) {
    // Skip authenticated tests if no token provided
    console.log('Skipping trips GET - no AUTH_TOKEN provided');
    sleep(1);
    return;
  }

  const startTime = Date.now();
  const res = http.get(`${BASE_URL}/api/trips`, {
    headers: authHeaders(),
  });
  tripsGetLatency.add(Date.now() - startTime);
  requestCount.add(1);

  const passed = check(res, {
    'trips GET status is 200': (r) => r.status === 200,
    'trips response is array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body) || (body.data && Array.isArray(body.data));
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!passed);
  sleep(1);
}

// Scenario 3: Trips POST
export function tripsPost() {
  if (!AUTH_TOKEN) {
    // Skip authenticated tests if no token provided
    console.log('Skipping trips POST - no AUTH_TOKEN provided');
    sleep(1);
    return;
  }

  // Sample trip creation payload
  const tripPayload = JSON.stringify({
    title: `k6 Load Test Trip ${Date.now()}`,
    destinations: [
      {
        country: 'Japan',
        city: 'Tokyo',
      },
    ],
    travelerDetails: {
      nationality: 'US',
      residenceCountry: 'US',
      partySize: 2,
    },
    tripDetails: {
      departureDate: '2025-06-01',
      returnDate: '2025-06-14',
      budget: 5000,
      budgetCurrency: 'USD',
      tripPurposes: ['leisure'],
    },
    preferences: {
      travelStyle: 'balanced',
      interests: ['culture', 'food'],
    },
  });

  const startTime = Date.now();
  const res = http.post(`${BASE_URL}/api/trips`, tripPayload, {
    headers: authHeaders(),
  });
  tripsPostLatency.add(Date.now() - startTime);
  requestCount.add(1);

  const passed = check(res, {
    'trips POST status is 200 or 201': (r) => r.status === 200 || r.status === 201,
    'trips POST returns id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.id || body.data?.id;
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!passed);

  // Clean up - delete the test trip if created
  if (res.status === 200 || res.status === 201) {
    try {
      const body = JSON.parse(res.body);
      const tripId = body.id || body.data?.id;
      if (tripId) {
        http.del(`${BASE_URL}/api/trips/${tripId}`, null, {
          headers: authHeaders(),
        });
      }
    } catch {
      // Ignore cleanup errors
    }
  }

  sleep(2);
}

// Setup - verify connectivity
export function setup() {
  console.log('=== TIP API Performance Baseline ===');
  console.log(`Target: ${BASE_URL}`);
  console.log(`Auth Token: ${AUTH_TOKEN ? 'Provided' : 'Not provided (authenticated tests will be skipped)'}`);
  console.log('');
  console.log('Performance Targets:');
  console.log('  - /api/health: p95 < 100ms');
  console.log('  - /api/trips (GET): p95 < 500ms');
  console.log('  - /api/trips (POST): p95 < 2000ms');
  console.log('');

  // Verify connectivity
  const res = http.get(`${BASE_URL}/api/health`);
  if (res.status !== 200) {
    throw new Error(`Cannot connect to ${BASE_URL}. Health check returned ${res.status}`);
  }

  return { startTime: new Date().toISOString() };
}

// Teardown - print summary
export function teardown(data) {
  console.log('');
  console.log('=== Test Complete ===');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
}

// Custom summary handler
export function handleSummary(data) {
  const results = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    duration_seconds: data.state.testRunDurationMs / 1000,
    total_requests: data.metrics.request_count ? data.metrics.request_count.values.count : 0,
    error_rate: data.metrics.errors ? (data.metrics.errors.values.rate * 100).toFixed(2) + '%' : '0%',
    thresholds: {
      health_p95: {
        target: '< 100ms',
        actual: data.metrics.health_latency
          ? data.metrics.health_latency.values['p(95)'].toFixed(2) + 'ms'
          : 'N/A',
        passed: data.metrics.health_latency
          ? data.metrics.health_latency.values['p(95)'] < 100
          : false,
      },
      trips_get_p95: {
        target: '< 500ms',
        actual: data.metrics.trips_get_latency
          ? data.metrics.trips_get_latency.values['p(95)'].toFixed(2) + 'ms'
          : 'N/A (skipped)',
        passed: data.metrics.trips_get_latency
          ? data.metrics.trips_get_latency.values['p(95)'] < 500
          : true, // Pass if skipped
      },
      trips_post_p95: {
        target: '< 2000ms',
        actual: data.metrics.trips_post_latency
          ? data.metrics.trips_post_latency.values['p(95)'].toFixed(2) + 'ms'
          : 'N/A (skipped)',
        passed: data.metrics.trips_post_latency
          ? data.metrics.trips_post_latency.values['p(95)'] < 2000
          : true, // Pass if skipped
      },
    },
  };

  const allPassed =
    results.thresholds.health_p95.passed &&
    results.thresholds.trips_get_p95.passed &&
    results.thresholds.trips_post_p95.passed;

  results.overall = allPassed ? 'PASS' : 'FAIL';

  console.log('\n=== Performance Baseline Results ===\n');
  console.log(`Duration: ${results.duration_seconds.toFixed(1)} seconds`);
  console.log(`Total Requests: ${results.total_requests}`);
  console.log(`Error Rate: ${results.error_rate}`);
  console.log('');
  console.log('Threshold Results:');
  console.log(`  Health (p95 < 100ms): ${results.thresholds.health_p95.actual} - ${results.thresholds.health_p95.passed ? 'PASS' : 'FAIL'}`);
  console.log(`  Trips GET (p95 < 500ms): ${results.thresholds.trips_get_p95.actual} - ${results.thresholds.trips_get_p95.passed ? 'PASS' : 'FAIL'}`);
  console.log(`  Trips POST (p95 < 2000ms): ${results.thresholds.trips_post_p95.actual} - ${results.thresholds.trips_post_p95.passed ? 'PASS' : 'FAIL'}`);
  console.log('');
  console.log(`Overall: ${results.overall}`);

  return {
    stdout: JSON.stringify(results, null, 2),
    'tests/load/baseline-results.json': JSON.stringify(results, null, 2),
  };
}
