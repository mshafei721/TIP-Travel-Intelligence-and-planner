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
    # Validate trip_id
    if not trip_id or trip_id.strip() == "":
        raise ValueError("trip_id is required and cannot be empty")

    print(f"[Task {self.request.id}] Executing Orchestrator for trip {trip_id}")

    # TODO: Implement Orchestrator logic in Phase 2
    # - Create agent job records
    # - Dispatch parallel agent tasks
    # - Monitor agent progress
    # - Aggregate results
    # - Generate final report structure

    result = {
        "trip_id": trip_id,
        "status": "placeholder",
        "agents_executed": [],
        "total_duration": 0.0,
        "error": None,
    }

    print(f"[Task {self.request.id}] Completed Orchestrator for trip {trip_id}")
    return result


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
