/**
 * TIP - Smoke Test
 *
 * Quick validation that the API is responding correctly.
 * Run this before full load tests.
 *
 * Usage:
 *   k6 run tests/load/smoke-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'https://tip-travel-intelligence-and-planner-production.up.railway.app';

export const options = {
  vus: 1,
  duration: '10s',
  thresholds: {
    http_req_duration: ['p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  // Test health endpoint
  const healthRes = http.get(`${BASE_URL}/api/health`);
  check(healthRes, {
    'health is 200': (r) => r.status === 200,
    'health has status': (r) => JSON.parse(r.body).status === 'healthy',
  });

  sleep(1);

  // Test ready endpoint
  const readyRes = http.get(`${BASE_URL}/api/health/ready`);
  check(readyRes, {
    'ready is 200': (r) => r.status === 200,
  });

  sleep(1);

  // Test live endpoint
  const liveRes = http.get(`${BASE_URL}/api/health/live`);
  check(liveRes, {
    'live is 200': (r) => r.status === 200,
  });

  sleep(1);
}
