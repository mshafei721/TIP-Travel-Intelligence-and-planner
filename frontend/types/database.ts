export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: '14.1';
  };
  public: {
    Tables: {
      user_profiles: {
        Row: {
          avatar_url: string | null;
          created_at: string;
          display_name: string | null;
          id: string;
          preferences: Json;
          updated_at: string;
        };
        Insert: {
          avatar_url?: string | null;
          created_at?: string;
          display_name?: string | null;
          id: string;
          preferences?: Json;
          updated_at?: string;
        };
        Update: {
          avatar_url?: string | null;
          created_at?: string;
          display_name?: string | null;
          id?: string;
          preferences?: Json;
          updated_at?: string;
        };
      };
      traveler_profiles: {
        Row: {
          accessibility_needs: string | null;
          created_at: string;
          date_of_birth: string | null;
          dietary_restrictions: Json;
          id: string;
          nationality: string;
          residency_country: string;
          residency_status: string;
          travel_style: string;
          updated_at: string;
          user_id: string;
        };
        Insert: {
          accessibility_needs?: string | null;
          created_at?: string;
          date_of_birth?: string | null;
          dietary_restrictions?: Json;
          id?: string;
          nationality: string;
          residency_country: string;
          residency_status: string;
          travel_style: string;
          updated_at?: string;
          user_id: string;
        };
        Update: {
          accessibility_needs?: string | null;
          created_at?: string;
          date_of_birth?: string | null;
          dietary_restrictions?: Json;
          id?: string;
          nationality?: string;
          residency_country?: string;
          residency_status?: string;
          travel_style?: string;
          updated_at?: string;
          user_id?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
    CompositeTypes: {
      [_ in never]: never;
    };
  };
};
