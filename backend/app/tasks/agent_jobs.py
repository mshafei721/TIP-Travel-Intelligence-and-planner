"""
Agent job execution tasks

These tasks handle async execution of AI agents for report generation:
- Orchestrator coordination
- Individual agent execution (visa, country, weather, etc.)
- Result aggregation and storage

Each agent job is tracked in the agent_jobs table with status updates.
"""

from typing import Any

from celery import shared_task

from app.core.celery_app import BaseTipTask


def _get_field(data: dict, *field_names: str, default: Any = None) -> Any:
    """
    Get a field from a dict, trying multiple field name variants.
    Handles camelCase (frontend) and snake_case (backend) naming conventions.

    Args:
        data: The dictionary to extract from
        field_names: Field names to try in order (e.g., "departure_date", "departureDate")
        default: Default value if no field is found

    Returns:
        The field value or default
    """
    for name in field_names:
        if name in data and data[name] is not None:
            return data[name]
    return default


def _normalize_trip_data(trip: dict) -> dict:
    """
    Normalize trip data field names from database format (camelCase in JSONB)
    to backend format (snake_case).

    This handles the mismatch between frontend (camelCase) and backend (snake_case).
    """
    traveler = trip.get("traveler_details", {})
    destinations = trip.get("destinations", [])
    details = trip.get("trip_details", {})
    preferences = trip.get("preferences", {})

    # Get primary destination
    primary_dest = destinations[0] if destinations else {}

    # Normalize traveler details
    normalized_traveler = {
        "name": traveler.get("name", ""),
        "email": traveler.get("email", ""),
        "age": traveler.get("age"),
        "nationality": traveler.get("nationality", "US"),
        "residence_country": _get_field(traveler, "residence_country", "residenceCountry", default="US"),
        "origin_city": _get_field(traveler, "origin_city", "originCity", default=""),
        "residency_status": _get_field(traveler, "residency_status", "residencyStatus", default=""),
        "party_size": _get_field(traveler, "party_size", "partySize", default=1),
        "party_ages": _get_field(traveler, "party_ages", "partyAges", default=[]),
        "contact_preferences": _get_field(traveler, "contact_preferences", "contactPreferences", default=[]),
    }

    # Normalize trip details
    departure_date = _get_field(details, "departure_date", "departureDate")
    return_date = _get_field(details, "return_date", "returnDate")

    # Handle tripPurposes (array) vs trip_purpose (string)
    trip_purposes = _get_field(details, "tripPurposes", "trip_purposes", default=[])
    trip_purpose = _get_field(details, "trip_purpose", "tripPurpose")
    if not trip_purpose and trip_purposes:
        trip_purpose = trip_purposes[0] if isinstance(trip_purposes, list) else trip_purposes
    trip_purpose = (trip_purpose or "tourism").lower()

    normalized_details = {
        "departure_date": departure_date,
        "return_date": return_date,
        "budget": details.get("budget", 1000),
        "currency": details.get("currency", "USD"),
        "trip_purpose": trip_purpose,
        "trip_purposes": trip_purposes,
    }

    # Normalize preferences
    normalized_preferences = {
        "travel_style": _get_field(preferences, "travel_style", "travelStyle", default="balanced"),
        "interests": preferences.get("interests", []),
        "dietary_restrictions": _get_field(preferences, "dietary_restrictions", "dietaryRestrictions", default=[]),
        "accessibility_needs": _get_field(preferences, "accessibility_needs", "accessibilityNeeds", default=""),
        "accommodation_type": _get_field(preferences, "accommodation_type", "accommodationType", default="hotel"),
        "transportation_preference": _get_field(preferences, "transportation_preference", "transportationPreference", default="any"),
    }

    return {
        "trip_id": trip.get("id"),
        "user_id": trip.get("user_id"),
        "title": trip.get("title"),
        "status": trip.get("status"),
        "traveler": normalized_traveler,
        "destination": {
            "country": primary_dest.get("country", "Unknown"),
            "city": primary_dest.get("city", "Unknown"),
        },
        "destinations": destinations,
        "details": normalized_details,
        "preferences": normalized_preferences,
        "raw": trip,  # Keep raw data for debugging
    }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_agent_job",
    time_limit=1800,  # 30 minutes
)
def execute_agent_job(
    self, job_id: str, agent_type: str, input_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Execute an individual agent job

    Args:
        job_id: Agent job ID from database
        agent_type: Type of agent to execute (visa, country, weather, etc.)
        input_data: Agent input parameters

    Returns:
        Agent execution results including data, confidence, sources

    Raises:
        ValueError: If agent_type is invalid

    Flow:
        1. Update job status to 'running'
        2. Initialize agent based on agent_type
        3. Execute agent with input_data
        4. Store results in report_sections table
        5. Update job status to 'completed' or 'failed'
    """
    # Validate agent type
    valid_agent_types = [
        "visa",
        "country",
        "weather",
        "currency",
        "culture",
        "food",
        "attractions",
        "itinerary",
        "flight",
        "orchestrator",
    ]
    if agent_type not in valid_agent_types:
        raise ValueError(f"Invalid agent type: {agent_type}. Must be one of {valid_agent_types}")

    print(f"[Task {self.request.id}] Executing {agent_type} agent for job {job_id}")

    # TODO: Implement agent execution logic in Phase 2 (Agents)
    # For now, return placeholder result
    result = {
        "job_id": job_id,
        "agent_type": agent_type,
        "status": "placeholder",
        "data": {},
        "confidence": 0.0,
        "sources": [],
        "error": None,
    }

    print(f"[Task {self.request.id}] Completed {agent_type} agent for job {job_id}")
    return result


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_visa_agent",
    time_limit=1800,  # 30 minutes
)
def execute_visa_agent(self, trip_id: str, traveler_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Visa Agent for visa requirements analysis

    Args:
        trip_id: Trip ID from database
        traveler_data: Traveler profile and trip details including:
            - user_nationality: ISO Alpha-2 code
            - destination_country: ISO Alpha-2 code
            - destination_city: str
            - trip_purpose: str (tourism, business, transit)
            - duration_days: int
            - departure_date: str (ISO format)

    Returns:
        Visa requirements analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required traveler_data fields are missing

    Production implementation using CrewAI + Travel Buddy AI.
    """
    from datetime import date

    from app.agents.visa.agent import VisaAgent
    from app.agents.visa.models import VisaAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Visa Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "user_nationality",
            "destination_country",
            "destination_city",
            "duration_days",
            "departure_date",
        ]
        for field in required_fields:
            if field not in traveler_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse departure_date
        departure_date_str = traveler_data["departure_date"]
        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        # Create VisaAgentInput
        input_data = VisaAgentInput(
            trip_id=trip_id,
            user_nationality=traveler_data["user_nationality"],
            destination_country=traveler_data["destination_country"],
            destination_city=traveler_data["destination_city"],
            trip_purpose=traveler_data.get("trip_purpose", "tourism"),
            duration_days=traveler_data["duration_days"],
            departure_date=departure_date,
            traveler_count=traveler_data.get("traveler_count", 1),
        )

        # Initialize and run Visa Agent
        agent = VisaAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "visa",
                    "title": "Visa Requirements",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": [source.model_dump() for source in result.sources],
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store visa report in database")

        print(f"[Task {self.request.id}] Completed Visa Agent for trip {trip_id}")
        print(f"[Task {self.request.id}] Confidence: {result.confidence}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "visa",
            "status": "completed",
            "data": result.data,
            "confidence": result.confidence,
            "sources": result.sources,
            "execution_time": result.execution_time,
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Visa Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "visa",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_country_agent",
    time_limit=1800,  # 30 minutes
)
def execute_country_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Country Agent for comprehensive country intelligence

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name or ISO code)
            - destination_city: str (optional)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - traveler_nationality: str (optional)

    Returns:
        Country intelligence analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI + REST Countries API.
    """
    from datetime import date

    from app.agents.country.agent import CountryAgent
    from app.agents.country.models import CountryAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Country Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create CountryAgentInput
        input_data = CountryAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("traveler_nationality"),
        )

        # Initialize and run Country Agent
        agent = CountryAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence_score * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "country",
                    "title": f"Country Information: {result.country_name}",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": [source.model_dump() for source in result.sources],
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store country report in database")

        print(f"[Task {self.request.id}] Completed Country Agent for trip {trip_id}")
        print(f"[Task {self.request.id}] Country: {result.country_name}")
        print(f"[Task {self.request.id}] Confidence: {result.confidence_score}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "country",
            "status": "completed",
            "data": content_data,
            "confidence": result.confidence_score,
            "sources": [source.model_dump() for source in result.sources],
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Country Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "country",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_weather_agent",
    time_limit=1800,  # 30 minutes
)
def execute_weather_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Weather Agent for comprehensive weather intelligence

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (city name)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - user_nationality: str (optional, ISO Alpha-2)
            - latitude: float (optional)
            - longitude: float (optional)

    Returns:
        Weather intelligence analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI + Visual Crossing Weather API.
    """
    from datetime import date

    from app.agents.weather.agent import WeatherAgent
    from app.agents.weather.models import WeatherAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Weather Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "destination_city",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create WeatherAgentInput
        input_data = WeatherAgentInput(
            trip_id=trip_id,
            user_nationality=trip_data.get("user_nationality", "US"),
            destination_country=trip_data["destination_country"],
            destination_city=trip_data["destination_city"],
            departure_date=departure_date,
            return_date=return_date,
            latitude=trip_data.get("latitude"),
            longitude=trip_data.get("longitude"),
        )

        # Initialize and run Weather Agent
        agent = WeatherAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence_score * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "weather",
                    "title": f"Weather Forecast: {result.location}",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": result.sources,
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store weather report in database")

        print(f"[Task {self.request.id}] Completed Weather Agent for trip {trip_id}")
        print(f"[Task {self.request.id}] Location: {result.location}")
        print(f"[Task {self.request.id}] Average Temp: {result.average_temp}°C")
        print(f"[Task {self.request.id}] Confidence: {result.confidence_score}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "weather",
            "status": "completed",
            "data": content_data,
            "confidence": result.confidence_score,
            "sources": result.sources,
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Weather Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "weather",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_orchestrator",
    time_limit=3600,  # 60 minutes
)
def execute_orchestrator(self, trip_id: str) -> dict[str, Any]:
    """
    Execute Orchestrator Agent to coordinate all sub-agents

    Args:
        trip_id: Trip ID from database

    Returns:
        Orchestrator execution summary with all agent results

    Raises:
        ValueError: If trip_id is missing or empty

    Flow:
        1. Load trip data and traveler profile
        2. Create agent jobs in database
        3. Dispatch agents in parallel (visa, country, weather, etc.)
        4. Wait for all agents to complete
        5. Aggregate results into report sections
        6. Mark trip report as ready
    """
    import asyncio
    import time
    from datetime import datetime

    from app.agents.orchestrator.agent import OrchestratorAgent
    from app.core.supabase import supabase

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise ValueError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Orchestrator for trip {trip_id}")
    start_time = time.time()

    try:
        # Step 1: Load trip data from database
        trip_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise ValueError(f"Trip {trip_id} not found")

        trip = trip_response.data[0]
        print(f"[Task {self.request.id}] Loaded trip data for {trip_id}")

        # Step 2: Normalize trip data (handles camelCase/snake_case mismatch)
        normalized = _normalize_trip_data(trip)
        print(f"[Task {self.request.id}] Normalized trip data")

        # Validate required dates before proceeding
        departure_date = normalized["details"]["departure_date"]
        return_date = normalized["details"]["return_date"]

        if not departure_date or not return_date:
            error_msg = "Cannot generate report: trip dates are required. Please set departure and return dates for your trip."
            print(f"[Task {self.request.id}] Validation failed: {error_msg}")

            # Update trip status to failed with clear error
            supabase.table("trips").update({
                "status": "failed",
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", trip_id).execute()

            return {
                "trip_id": trip_id,
                "status": "failed",
                "agents_executed": [],
                "total_duration": 0,
                "sections": {},
                "errors": [{"error": error_msg, "code": "MISSING_DATES"}],
                "error": error_msg,
            }

        # Build orchestrator input using normalized data
        orchestrator_input = {
            "trip_id": trip_id,
            "user_nationality": normalized["traveler"]["nationality"],
            "destination_country": normalized["destination"]["country"],
            "destination_city": normalized["destination"]["city"],
            "departure_date": departure_date,
            "return_date": return_date,
            "trip_purpose": normalized["details"]["trip_purpose"],
        }

        print(f"[Task {self.request.id}] Prepared orchestrator input: {orchestrator_input}")

        # Step 3: Update trip status to processing
        supabase.table("trips").update({
            "status": "processing",
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", trip_id).execute()

        # Step 4: Create orchestrator job record
        job_response = supabase.table("agent_jobs").insert({
            "trip_id": trip_id,
            "agent_type": "orchestrator",
            "status": "running",
            "input_data": orchestrator_input,
            "celery_task_id": str(self.request.id),
            "started_at": datetime.utcnow().isoformat(),
        }).execute()

        job_id = job_response.data[0]["id"] if job_response.data else None
        print(f"[Task {self.request.id}] Created agent job: {job_id}")

        # Step 5: Initialize and run Orchestrator Agent
        orchestrator = OrchestratorAgent()
        print(f"[Task {self.request.id}] Available agents: {orchestrator.list_available_agents()}")

        # Run the async generate_report method
        # Use asyncio.run() for synchronous context
        result = asyncio.run(orchestrator.generate_report(orchestrator_input))

        # Step 6: Update trip status to completed
        execution_time = time.time() - start_time
        supabase.table("trips").update({
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", trip_id).execute()

        # Update agent job to completed
        if job_id:
            supabase.table("agent_jobs").update({
                "status": "completed",
                "result_data": result,
                "completed_at": datetime.utcnow().isoformat(),
            }).eq("id", job_id).execute()

        print(f"[Task {self.request.id}] Completed Orchestrator for trip {trip_id}")
        print(f"[Task {self.request.id}] Execution time: {execution_time:.2f}s")
        print(f"[Task {self.request.id}] Sections generated: {list(result.get('sections', {}).keys())}")

        return {
            "trip_id": trip_id,
            "status": "completed",
            "agents_executed": list(result.get("sections", {}).keys()),
            "total_duration": execution_time,
            "sections": result.get("sections", {}),
            "errors": result.get("errors", []),
            "error": None,
        }

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        print(f"[Task {self.request.id}] Error in Orchestrator: {error_msg}")

        # Update trip status to failed
        try:
            supabase.table("trips").update({
                "status": "failed",
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", trip_id).execute()
        except Exception:
            pass

        return {
            "trip_id": trip_id,
            "status": "failed",
            "agents_executed": [],
            "total_duration": execution_time,
            "sections": {},
            "errors": [{"error": error_msg}],
            "error": error_msg,
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_currency_agent",
    time_limit=1800,  # 30 minutes
)
def execute_currency_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Currency Agent for currency and financial intelligence

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (optional, city name)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - user_nationality: str (optional, ISO Alpha-2)
            - base_currency: str (optional, defaults to USD)

    Returns:
        Currency intelligence analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI + fawazahmed0/exchange-api.
    """
    from datetime import date

    from app.agents.currency.agent import CurrencyAgent
    from app.agents.currency.models import CurrencyAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Currency Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create CurrencyAgentInput
        input_data = CurrencyAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("user_nationality", "US"),
            base_currency=trip_data.get("base_currency", "USD"),
        )

        # Initialize and run Currency Agent
        agent = CurrencyAgent()
        result = agent.run(input_data)

        # Return structured response
        return {
            "trip_id": trip_id,
            "agent_type": result.agent_type,
            "status": "success",
            "data": result.model_dump(mode="json"),
            "confidence": result.confidence_score,
            "sources": [s.model_dump() for s in result.sources],
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Currency Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "currency",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_culture_agent",
    time_limit=1800,  # 30 minutes
)
def execute_culture_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Culture Agent for cultural intelligence and etiquette guidance

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (optional, city name)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - traveler_nationality: str (optional, ISO Alpha-2)

    Returns:
        Cultural intelligence analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI with cultural knowledge bases.
    """
    from datetime import date

    from app.agents.culture.agent import CultureAgent
    from app.agents.culture.models import CultureAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Culture Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create CultureAgentInput
        input_data = CultureAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("traveler_nationality"),
        )

        # Initialize and run Culture Agent
        agent = CultureAgent()
        result = agent.run(input_data)

        # Return structured response
        return {
            "trip_id": trip_id,
            "agent_type": result.agent_type,
            "status": "success",
            "data": result.model_dump(mode="json"),
            "confidence": result.confidence_score,
            "sources": [s.model_dump() for s in result.sources],
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Culture Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "culture",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_food_agent",
    time_limit=1800,  # 30 minutes
)
def execute_food_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Food Agent for culinary intelligence and food recommendations

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (optional, city name)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - traveler_nationality: str (optional, ISO Alpha-2)
            - dietary_restrictions: list[str] (optional, e.g., vegetarian, vegan)

    Returns:
        Culinary intelligence analysis with confidence and sources

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI with culinary knowledge bases.
    """
    from datetime import date

    from app.agents.food.agent import FoodAgent
    from app.agents.food.models import FoodAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Food Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create FoodAgentInput
        input_data = FoodAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("traveler_nationality"),
            dietary_restrictions=trip_data.get("dietary_restrictions"),
        )

        # Initialize and run Food Agent
        agent = FoodAgent()
        result = agent.run(input_data)

        # Return structured response
        return {
            "trip_id": trip_id,
            "agent_type": result.agent_type,
            "status": "success",
            "data": result.model_dump(mode="json"),
            "confidence": result.confidence_score,
            "sources": [s.model_dump() for s in result.sources],
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Food Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "food",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_attractions_agent",
    time_limit=1800,  # 30 minutes
)
def execute_attractions_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Attractions Agent for tourist attractions and points of interest

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (optional)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - traveler_nationality: str (optional)
            - interests: list[str] (optional: history, art, culture, nature, food)

    Returns:
        Attractions intelligence with top attractions, hidden gems, day trips

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI + OpenTripMap API.
    """
    from datetime import date

    from app.agents.attractions.agent import AttractionsAgent
    from app.agents.attractions.models import AttractionsAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Attractions Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create AttractionsAgentInput
        input_data = AttractionsAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("traveler_nationality"),
            interests=trip_data.get("interests"),
        )

        # Initialize and run Attractions Agent
        agent = AttractionsAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence_score * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "attractions",
                    "title": f"Attractions: {trip_data.get('destination_city') or trip_data['destination_country']}",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": [source.model_dump() for source in result.sources],
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store attractions report in database")

        print(f"[Task {self.request.id}] Completed Attractions Agent for trip {trip_id}")
        print(f"[Task {self.request.id}] Destination: {trip_data.get('destination_city') or trip_data['destination_country']}")
        print(f"[Task {self.request.id}] Attractions found: {len(result.top_attractions)}")
        print(f"[Task {self.request.id}] Confidence: {result.confidence_score}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "attractions",
            "status": "completed",
            "data": content_data,
            "confidence": result.confidence_score,
            "sources": [source.model_dump() for source in result.sources],
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Attractions Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "attractions",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_itinerary_agent",
    time_limit=2400,  # 40 minutes (longer for complex planning)
)
def execute_itinerary_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Itinerary Agent for comprehensive trip itinerary generation

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - destination_country: str (country name)
            - destination_city: str (optional)
            - departure_date: str (ISO format)
            - return_date: str (ISO format)
            - traveler_nationality: str (optional)
            - group_size: int (optional)
            - traveler_ages: list[int] (optional)
            - budget_level: str (budget, mid-range, luxury)
            - pace: str (relaxed, moderate, packed)
            - interests: list[str] (optional)
            - mobility_constraints: list[str] (optional)
            - dietary_restrictions: list[str] (optional)
            - visa_info: dict (optional - from VisaAgent)
            - country_info: dict (optional - from CountryAgent)
            - weather_info: dict (optional - from WeatherAgent)
            - attractions_info: dict (optional - from AttractionsAgent)

    Returns:
        Comprehensive itinerary with daily plans, accommodations, costs

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI for AI-powered itinerary generation.
    Synthesizes data from all other agents to create optimized day-by-day plans.
    """
    from datetime import date

    from app.agents.itinerary.agent import ItineraryAgent
    from app.agents.itinerary.models import ItineraryAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Itinerary Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "destination_country",
            "departure_date",
            "return_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data["return_date"]

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        if isinstance(return_date_str, str):
            return_date = date.fromisoformat(return_date_str)
        else:
            return_date = return_date_str

        # Create ItineraryAgentInput
        input_data = ItineraryAgentInput(
            trip_id=trip_id,
            destination_country=trip_data["destination_country"],
            destination_city=trip_data.get("destination_city"),
            departure_date=departure_date,
            return_date=return_date,
            traveler_nationality=trip_data.get("traveler_nationality"),
            group_size=trip_data.get("group_size", 1),
            traveler_ages=trip_data.get("traveler_ages"),
            budget_level=trip_data.get("budget_level", "mid-range"),
            pace=trip_data.get("pace", "moderate"),
            interests=trip_data.get("interests"),
            mobility_constraints=trip_data.get("mobility_constraints"),
            dietary_restrictions=trip_data.get("dietary_restrictions"),
            visa_info=trip_data.get("visa_info"),
            country_info=trip_data.get("country_info"),
            weather_info=trip_data.get("weather_info"),
            attractions_info=trip_data.get("attractions_info"),
        )

        # Initialize and run Itinerary Agent
        agent = ItineraryAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence_score * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "itinerary",
                    "title": f"Itinerary: {trip_data.get('destination_city') or trip_data['destination_country']}",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": [source.model_dump() for source in result.sources],
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store itinerary report in database")

        trip_duration = (return_date - departure_date).days
        print(f"[Task {self.request.id}] Completed Itinerary Agent for trip {trip_id}")
        print(f"[Task {self.request.id}] Destination: {trip_data.get('destination_city') or trip_data['destination_country']}")
        print(f"[Task {self.request.id}] Duration: {trip_duration} days")
        print(f"[Task {self.request.id}] Daily plans: {len(result.daily_plans)}")
        print(f"[Task {self.request.id}] Confidence: {result.confidence_score}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "itinerary",
            "status": "completed",
            "data": content_data,
            "confidence": result.confidence_score,
            "sources": [source.model_dump() for source in result.sources],
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Itinerary Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "itinerary",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_flight_agent",
    time_limit=1800,  # 30 minutes
)
def execute_flight_agent(self, trip_id: str, trip_data: dict[str, Any]) -> dict[str, Any]:
    """
    Execute Flight Agent for flight search and booking recommendations

    Args:
        trip_id: Trip ID from database
        trip_data: Trip details including:
            - origin_city: str (departure city)
            - destination_city: str (arrival city)
            - departure_date: str (ISO format)
            - return_date: str (ISO format, optional for one-way)
            - passengers: int (default: 1)
            - cabin_class: str (economy, premium_economy, business, first)
            - budget_usd: float (optional)
            - direct_flights_only: bool (default: False)
            - flexible_dates: bool (default: True)

    Returns:
        Flight recommendations with pricing, booking guidance, and airport info

    Raises:
        KeyError: If trip_id is missing or empty
        ValueError: If required trip_data fields are missing

    Production implementation using CrewAI for AI-powered flight search.
    In production, integrate with Amadeus Self-Service API or similar for real-time data.
    """
    from datetime import date

    from app.agents.flight.agent import FlightAgent
    from app.agents.flight.models import CabinClass, FlightAgentInput

    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise KeyError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Flight Agent for trip {trip_id}")

    try:
        # Validate required fields
        required_fields = [
            "origin_city",
            "destination_city",
            "departure_date",
        ]
        for field in required_fields:
            if field not in trip_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse dates
        departure_date_str = trip_data["departure_date"]
        return_date_str = trip_data.get("return_date")

        if isinstance(departure_date_str, str):
            departure_date = date.fromisoformat(departure_date_str)
        else:
            departure_date = departure_date_str

        return_date = None
        if return_date_str:
            if isinstance(return_date_str, str):
                return_date = date.fromisoformat(return_date_str)
            else:
                return_date = return_date_str

        # Parse cabin class
        cabin_class_str = trip_data.get("cabin_class", "economy")
        try:
            cabin_class = CabinClass(cabin_class_str)
        except ValueError:
            cabin_class = CabinClass.ECONOMY

        # Create FlightAgentInput
        input_data = FlightAgentInput(
            trip_id=trip_id,
            origin_city=trip_data["origin_city"],
            destination_city=trip_data["destination_city"],
            departure_date=departure_date,
            return_date=return_date,
            passengers=trip_data.get("passengers", 1),
            cabin_class=cabin_class,
            budget_usd=trip_data.get("budget_usd"),
            direct_flights_only=trip_data.get("direct_flights_only", False),
            flexible_dates=trip_data.get("flexible_dates", True),
        )

        # Initialize and run Flight Agent
        agent = FlightAgent()
        result = agent.run(input_data)

        # Store result in database (Supabase report_sections table)
        from app.core.supabase import supabase

        # Convert result to dict for JSON storage
        content_data = result.model_dump(mode="json")

        # Convert confidence (0.0-1.0) to integer (0-100) for database
        confidence_integer = int(result.confidence_score * 100)

        # Store in report_sections table
        report_response = (
            supabase.table("report_sections")
            .insert(
                {
                    "trip_id": trip_id,
                    "section_type": "flight",
                    "title": f"Flights: {trip_data['origin_city']} → {trip_data['destination_city']}",
                    "content": content_data,
                    "confidence_score": confidence_integer,
                    "sources": [source.model_dump() for source in result.sources],
                    "generated_at": result.generated_at.isoformat(),
                }
            )
            .execute()
        )

        if not report_response.data:
            raise Exception("Failed to store flight report in database")

        trip_type = "round-trip" if return_date else "one-way"
        print(f"[Task {self.request.id}] Completed Flight Agent for trip {trip_id}")
        print(
            f"[Task {self.request.id}] Route: {trip_data['origin_city']} → {trip_data['destination_city']}"
        )
        print(f"[Task {self.request.id}] Type: {trip_type}")
        print(f"[Task {self.request.id}] Passengers: {input_data.passengers}")
        print(f"[Task {self.request.id}] Cabin: {cabin_class.value}")
        print(f"[Task {self.request.id}] Confidence: {result.confidence_score}")
        print(f"[Task {self.request.id}] Stored report ID: {report_response.data[0]['id']}")

        return {
            "trip_id": trip_id,
            "agent_type": "flight",
            "status": "completed",
            "data": content_data,
            "confidence": result.confidence_score,
            "sources": [source.model_dump() for source in result.sources],
            "error": None,
        }

    except Exception as e:
        print(f"[Task {self.request.id}] Error in Flight Agent: {str(e)}")
        return {
            "trip_id": trip_id,
            "agent_type": "flight",
            "status": "failed",
            "data": {},
            "confidence": 0.0,
            "sources": [],
            "error": str(e),
        }


# ============================================================================
# SELECTIVE RECALCULATION TASK
# ============================================================================


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.agent_jobs.execute_selective_recalc",
    time_limit=3600,  # 60 minutes for full recalc
)
def execute_selective_recalc(
    self, trip_id: str, agents_to_recalc: list[str]
) -> dict[str, Any]:
    """
    Execute selective recalculation for specified agents.

    This task re-runs only the specified agents based on detected changes,
    rather than regenerating the entire report.

    Args:
        trip_id: Trip ID from database
        agents_to_recalc: List of agent types to recalculate
            (e.g., ["visa", "weather", "itinerary"])

    Returns:
        Summary of recalculation results including:
        - trip_id: The trip that was recalculated
        - agents_recalculated: List of agents that were run
        - agent_results: Individual results per agent
        - overall_status: "completed" | "partial" | "failed"
        - errors: List of any errors encountered

    Flow:
        1. Fetch trip data from database
        2. Record recalculation job start
        3. For each agent in agents_to_recalc:
            a. Delete existing report section (if exists)
            b. Execute agent with current trip data
            c. Store new report section
            d. Update progress
        4. Update trip status based on results
        5. Record recalculation job completion
    """
    from app.core.supabase import supabase

    print(f"[Task {self.request.id}] Starting selective recalculation for trip {trip_id}")
    print(f"[Task {self.request.id}] Agents to recalculate: {agents_to_recalc}")

    results: dict[str, Any] = {
        "trip_id": trip_id,
        "agents_recalculated": agents_to_recalc,
        "agent_results": {},
        "overall_status": "completed",
        "errors": [],
    }

    try:
        # Fetch trip data
        trip_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise ValueError(f"Trip {trip_id} not found")

        trip = trip_response.data[0]

        # Record recalculation job start
        try:
            job_response = (
                supabase.table("recalculation_jobs")
                .insert({
                    "trip_id": trip_id,
                    "celery_task_id": str(self.request.id),
                    "agents_to_recalculate": agents_to_recalc,
                    "status": "in_progress",
                    "started_at": "now()",
                })
                .execute()
            )
            job_id = job_response.data[0]["id"] if job_response.data else None
        except Exception:
            job_id = None  # Table might not exist yet

        # Process each agent
        completed_agents = []
        failed_agents = []

        for agent_type in agents_to_recalc:
            try:
                print(f"[Task {self.request.id}] Recalculating {agent_type} agent...")

                # Delete existing report section
                supabase.table("report_sections").delete().eq(
                    "trip_id", trip_id
                ).eq("section_type", agent_type).execute()

                # Execute the appropriate agent task
                agent_result = _execute_single_agent(
                    task_id=str(self.request.id),
                    trip_id=trip_id,
                    trip_data=trip,
                    agent_type=agent_type,
                )

                results["agent_results"][agent_type] = agent_result

                if agent_result.get("status") == "completed":
                    completed_agents.append(agent_type)
                    print(f"[Task {self.request.id}] {agent_type} recalculation completed")
                else:
                    failed_agents.append(agent_type)
                    results["errors"].append(
                        f"{agent_type}: {agent_result.get('error', 'Unknown error')}"
                    )
                    print(f"[Task {self.request.id}] {agent_type} recalculation failed")

            except Exception as e:
                failed_agents.append(agent_type)
                results["errors"].append(f"{agent_type}: {str(e)}")
                results["agent_results"][agent_type] = {
                    "status": "failed",
                    "error": str(e),
                }
                print(f"[Task {self.request.id}] Error recalculating {agent_type}: {str(e)}")

        # Determine overall status
        if len(failed_agents) == 0:
            results["overall_status"] = "completed"
            trip_status = "completed"
        elif len(completed_agents) > 0:
            results["overall_status"] = "partial"
            trip_status = "completed"  # Partial success still counts
        else:
            results["overall_status"] = "failed"
            trip_status = "failed"

        # Update trip status
        supabase.table("trips").update({
            "status": trip_status,
        }).eq("id", trip_id).execute()

        # Update recalculation job if we have one
        if job_id:
            try:
                supabase.table("recalculation_jobs").update({
                    "status": results["overall_status"],
                    "completed_at": "now()",
                    "error_message": "; ".join(results["errors"]) if results["errors"] else None,
                }).eq("id", job_id).execute()
            except Exception:
                pass

        print(f"[Task {self.request.id}] Selective recalculation complete")
        print(f"[Task {self.request.id}] Completed: {completed_agents}")
        print(f"[Task {self.request.id}] Failed: {failed_agents}")

        return results

    except Exception as e:
        print(f"[Task {self.request.id}] Fatal error in selective recalculation: {str(e)}")

        # Try to update trip status
        try:
            supabase.table("trips").update({
                "status": "failed",
            }).eq("id", trip_id).execute()
        except Exception:
            pass

        results["overall_status"] = "failed"
        results["errors"].append(f"Fatal error: {str(e)}")
        return results


def _execute_single_agent(
    task_id: str, trip_id: str, trip_data: dict, agent_type: str
) -> dict[str, Any]:
    """
    Execute a single agent with the given trip data.

    This is a helper function that routes to the appropriate agent
    based on agent_type.
    """
    # Normalize trip data to handle camelCase/snake_case mismatch
    normalized = _normalize_trip_data(trip_data)

    # Common input data using normalized fields
    base_input = {
        "nationality": normalized["traveler"]["nationality"],
        "origin_city": normalized["traveler"]["origin_city"] or "New York",
        "destination_country": normalized["destination"]["country"],
        "destination_city": normalized["destination"]["city"],
        "departure_date": normalized["details"]["departure_date"],
        "return_date": normalized["details"]["return_date"],
        "budget": normalized["details"]["budget"],
        "currency": normalized["details"]["currency"],
        "trip_purpose": normalized["details"]["trip_purpose"],
        "interests": normalized["preferences"]["interests"],
        "dietary_restrictions": normalized["preferences"]["dietary_restrictions"],
        "travel_style": normalized["preferences"]["travel_style"],
    }

    # Route to appropriate agent (using synchronous execution for simplicity)
    # In production, you might want to call the actual agent tasks
    try:
        if agent_type == "visa":
            # Import and call visa agent directly
            try:
                from app.agents.visa.agent import VisaAgent
                from app.agents.visa.models import VisaAgentInput

                agent = VisaAgent()
                result = agent.run(VisaAgentInput(
                    user_nationality=base_input["nationality"],
                    destination_country=base_input["destination_country"],
                    destination_city=base_input["destination_city"],
                    trip_purpose=base_input["trip_purpose"],
                    duration_days=_calculate_duration(
                        base_input.get("departure_date"),
                        base_input.get("return_date"),
                    ),
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "weather":
            try:
                from app.agents.weather.agent import WeatherAgent
                from app.agents.weather.models import WeatherAgentInput

                agent = WeatherAgent()
                result = agent.run(WeatherAgentInput(
                    city=base_input["destination_city"],
                    country=base_input["destination_country"],
                    start_date=base_input.get("departure_date"),
                    end_date=base_input.get("return_date"),
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "currency":
            try:
                from app.agents.currency.agent import CurrencyAgent
                from app.agents.currency.models import CurrencyAgentInput

                agent = CurrencyAgent()
                result = agent.run(CurrencyAgentInput(
                    home_currency=base_input["currency"],
                    destination_country=base_input["destination_country"],
                    budget=base_input["budget"],
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "culture":
            try:
                from app.agents.culture.agent import CultureAgent
                from app.agents.culture.models import CultureAgentInput

                agent = CultureAgent()
                result = agent.run(CultureAgentInput(
                    destination_country=base_input["destination_country"],
                    destination_city=base_input["destination_city"],
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "food":
            try:
                from app.agents.food.agent import FoodAgent
                from app.agents.food.models import FoodAgentInput

                agent = FoodAgent()
                result = agent.run(FoodAgentInput(
                    destination_country=base_input["destination_country"],
                    destination_city=base_input["destination_city"],
                    dietary_restrictions=base_input.get("dietary_restrictions", []),
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "attractions":
            try:
                from app.agents.attractions.agent import AttractionsAgent
                from app.agents.attractions.models import AttractionsAgentInput

                agent = AttractionsAgent()
                result = agent.run(AttractionsAgentInput(
                    destination_city=base_input["destination_city"],
                    destination_country=base_input["destination_country"],
                    interests=base_input.get("interests", []),
                    budget_level=_budget_to_level(base_input["budget"]),
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "country":
            try:
                from app.agents.country.agent import CountryAgent
                from app.agents.country.models import CountryAgentInput

                agent = CountryAgent()
                result = agent.run(CountryAgentInput(
                    country_name=base_input["destination_country"],
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "itinerary":
            try:
                from app.agents.itinerary.agent import ItineraryAgent
                from app.agents.itinerary.models import ItineraryAgentInput

                agent = ItineraryAgent()
                result = agent.run(ItineraryAgentInput(
                    destination_city=base_input["destination_city"],
                    destination_country=base_input["destination_country"],
                    start_date=base_input.get("departure_date"),
                    end_date=base_input.get("return_date"),
                    interests=base_input.get("interests", []),
                    travel_style=base_input.get("travel_style", "balanced"),
                    budget=base_input["budget"],
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        elif agent_type == "flight":
            try:
                from app.agents.flight.agent import FlightAgent
                from app.agents.flight.models import FlightAgentInput

                agent = FlightAgent()
                result = agent.run(FlightAgentInput(
                    origin_city=base_input["origin_city"],
                    destination_city=base_input["destination_city"],
                    departure_date=base_input.get("departure_date"),
                    return_date=base_input.get("return_date"),
                ))
                return {"status": "completed", "data": result.model_dump(mode="json")}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        else:
            return {"status": "failed", "error": f"Unknown agent type: {agent_type}"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def _calculate_duration(departure_date: str | None, return_date: str | None) -> int:
    """Calculate trip duration in days."""
    if not departure_date or not return_date:
        return 7  # Default

    try:
        from datetime import datetime

        dep = datetime.fromisoformat(departure_date.replace("Z", "+00:00"))
        ret = datetime.fromisoformat(return_date.replace("Z", "+00:00"))
        return max(1, (ret - dep).days)
    except Exception:
        return 7


def _budget_to_level(budget: float) -> str:
    """Convert budget to level string."""
    if budget < 1000:
        return "budget"
    elif budget < 5000:
        return "moderate"
    else:
        return "luxury"
