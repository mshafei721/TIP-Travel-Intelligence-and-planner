import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import type { TripFormData } from '@/components/trip-wizard/TripCreationWizard';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const supabase = await createClient();

    // Get authenticated user session
    const {
      data: { session },
      error: authError,
    } = await supabase.auth.getSession();

    if (authError || !session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Parse request body
    const body: TripFormData = await request.json();

    // Forward to backend API
    const response = await fetch(`${BACKEND_URL}/api/trips`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({
        travelerDetails: body.travelerDetails,
        destinations: body.destinations,
        tripDetails: body.tripDetails,
        preferences: body.preferences,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create trip' }));
      console.error('Backend trip creation failed:', error);
      return NextResponse.json(
        { error: error.detail || 'Failed to create trip' },
        { status: response.status },
      );
    }

    const trip = await response.json();
    return NextResponse.json(trip);
  } catch (error) {
    console.error('Trip creation error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const supabase = await createClient();

    // Get authenticated user session
    const {
      data: { session },
      error: authError,
    } = await supabase.auth.getSession();

    if (authError || !session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Forward to backend API
    const response = await fetch(`${BACKEND_URL}/api/trips`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch trips' }));
      console.error('Backend trip fetch failed:', error);
      return NextResponse.json(
        { error: error.detail || 'Failed to fetch trips' },
        { status: response.status },
      );
    }

    const trips = await response.json();
    return NextResponse.json(trips);
  } catch (error) {
    console.error('Fetch trips error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
