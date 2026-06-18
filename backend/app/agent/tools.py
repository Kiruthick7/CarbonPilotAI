"""
tools.py
Gemini function-calling tool definitions for the CarbonPilot agent.
Tool schemas are defined here; implementations live in agent_service.py.
"""

from __future__ import annotations

from typing import Any

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "suggest_quick_replies",
            "description": (
                "Provide a list of 3-5 short clickable options for the user based on the question you just asked. "
                "Call this tool immediately after asking a question to render dynamic quick reply buttons in the UI."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of short quick reply options."
                    }
                },
                "required": ["options"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_footprint",
            "description": (
                "Calculate the user's carbon footprint from their profile data. "
                "Call this as soon as you have country + at least transport or diet data. "
                "Returns a full breakdown with category totals, peer percentile, and 1.5°C budget comparison. "
                "Always call this before presenting any numbers — never guess."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "description": "The user's CarbonProfile assembled from the conversation so far.",
                        "properties": {
                            "country_code": {"type": "string", "description": "ISO 3166-1 alpha-2 code, e.g. GB, US, IN"},
                            "transport": {"type": "object"},
                            "diet": {"type": "object"},
                            "home": {"type": "object"},
                            "consumption": {"type": "object"},
                        },
                    },
                },
                "required": ["profile"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_scenario",
            "description": (
                "Show the quantified impact of a specific lifestyle change. "
                "Returns CO₂ delta in tCO₂e/year, percentage change, financial impact, "
                "break-even timeline (for capital investments), and co-benefits. "
                "Use this to answer 'What if I went vegan?' or 'What if I bought an EV?'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario_type": {
                        "type": "string",
                        "enum": [
                            "switch_diet",
                            "switch_car",
                            "reduce_flights",
                            "switch_heating",
                            "add_renewable",
                            "reduce_consumption",
                        ],
                    },
                    "scenario_params": {
                        "type": "object",
                        "description": "Parameters specific to the scenario type.",
                    },
                },
                "required": ["scenario_type", "scenario_params"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rank_actions",
            "description": (
                "Generate a personalised, ranked list of up to 5 climate actions for the user. "
                "Ranked by impact/effort composite score. "
                "Respects user constraints (renter, budget, etc.). "
                "Call this after the footprint has been calculated."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "constraints": {
                        "type": "object",
                        "description": "Optional user constraints that filter out infeasible actions.",
                        "properties": {
                            "max_upfront_cost_usd": {"type": "number"},
                            "exclude_categories": {"type": "array", "items": {"type": "string"}},
                            "lifestyle_flags": {
                                "type": "object",
                                "properties": {
                                    "rents_home": {"type": "boolean"},
                                    "rural_location": {"type": "boolean"},
                                    "has_children": {"type": "boolean"},
                                },
                            },
                        },
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_constraint",
            "description": (
                "Record a user constraint that blocks a category of actions. "
                "Call this whenever a user expresses an inability or unwillingness to do something "
                "(e.g., 'I can't afford an EV', 'I rent so I can't install a heat pump', "
                "'I travel for work so I can't reduce flights'). "
                "This permanently excludes those actions from future recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "constraint_type": {
                        "type": "string",
                        "enum": ["rents_home", "rural_location", "no_budget", "work_travel", "medical_diet"],
                    },
                    "free_text": {
                        "type": "string",
                        "description": "The user's exact words expressing the constraint.",
                    },
                },
                "required": ["constraint_type"],
            },
        },
    },
]
