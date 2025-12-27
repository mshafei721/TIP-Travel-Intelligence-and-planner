import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import type { TripFormData } from '@/components/trip-wizard/TripCreationWizard';
import type { SupabaseClient } from '@supabase/supabase-js';

// Helper to access trips table (exists in DB but not yet fully typed)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getTripsTable(supabase: SupabaseClient<any>) {
  return supabase.from('trips');
}

export async function POST(request: Request) {
  try {
    const supabase = await createClient();

    // Get authenticated user
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Parse request body
    const body: TripFormData = await request.json();

    // Generate trip title from destination(s)
    const primaryDestination = body.destinations[0];
    const title = primaryDestination
      ? `Trip to ${primaryDestination.city}, ${primaryDestination.country}`
      : 'New Trip';

    // Insert trip into database
    const { data: trip, error: insertError } = await getTripsTable(supabase)
      .insert({
        user_id: user.id,
        title,
        status: 'pending',
        traveler_details: body.travelerDetails,
        destinations: body.destinations,
        trip_details: body.tripDetails,
        preferences: body.preferences,
      })
      .select()
      .single();

    if (insertError) {
      console.error('Failed to create trip:', insertError);
      return NextResponse.json({ error: insertError.message }, { status: 500 });
    }

    return NextResponse.json(trip);
  } catch (error) {
    console.error('Trip creation error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const supabase = await createClient();

    // Get authenticated user
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Fetch user's trips
    const { data: trips, error: fetchError } = await getTripsTable(supabase)
      .select('*')
      .eq('user_id', user.id)
      .is('deleted_at', null)
      .order('created_at', { ascending: false });

    if (fetchError) {
      console.error('Failed to fetch trips:', fetchError);
      return NextResponse.json({ error: fetchError.message }, { status: 500 });
    }

    return NextResponse.json(trips);
  } catch (error) {
    console.error('Fetch trips error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
