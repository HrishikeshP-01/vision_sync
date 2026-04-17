import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from pprint import pprint
import asyncio
import json
import base64

from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from ux_persona_agent.agent import ux_persona_agent
from ux_lead_agent.agent import ux_lead_agent

load_dotenv()


async def run_personas(selected_personas, video_part, app_name: str, user_id: str):
    session_service = InMemorySessionService()
    # Define initial state
    initial_state = {
        "company": f'{os.getenv("COMPANY")}',
        "persona": "",
        "background": "",
        "personality": "",
        "ux_likes": "",
        "ui_likes": "",
        "ux_dislikes": "",
        "ui_dislikes": "",
        "examples": ""
    }

    session = await session_service.create_session(
        app_name = app_name,
        user_id = user_id,
        state = initial_state
    )

    #print('Initial State:')
    #pprint(session.state)

    runner = Runner(
        agent=ux_persona_agent,
        app_name=app_name,
        session_service=session_service
        )

    # Load the personas & get the user surveys
    personas = None
    user_surveys = {}
    with open('input/personas.json', 'r') as f:
        personas = json.load(f)

    for persona in selected_personas:

        session.state['persona'] = persona
        attributes = personas[persona]
        for key in attributes.keys():
            session.state[key] = attributes[key]

        session = await session_service.create_session(
            app_name = app_name,
            user_id = user_id,
            state = session.state
        )
        #pprint(session.state)

        content = types.Content(role='user', parts=[video_part])

        # Execute agent event asynchronously using the agent runner
        # Session information is passed via user_id & session_id
        events = runner.run_async(
            user_id = session.user_id,
            session_id = session.id,
            new_message = content
        )

        async for event in events:
            #print(event)
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print(final_response)
                user_surveys[persona] = final_response

    #pprint(user_surveys)
    #with open('output/user_survey.json', 'w', encoding='utf-8') as f:
    #    json.dump(user_surveys, f, indent=4)

    session.state['user_surveys'] = user_surveys

    return session.state

async def get_ux_lead_analysis(state, video_part, app_name: str, user_id: str):
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name = app_name,
        user_id = user_id,
        state = state
    )

    runner = Runner(
        agent=ux_lead_agent,
        app_name=app_name,
        session_service=session_service
        )

    content = types.Content(role='user', parts=[video_part])

    events = runner.run_async(
            user_id = session.user_id,
            session_id = session.id,
            new_message = content
        )

    async for event in events:
        #print(event)
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print(final_response)
    
    results = session.state['user_surveys']
    results['UX Analysis'] = final_response

    return results 

async def generate_ux_analysis(selected_personas, video_part, app_name: str, user_id: str):
    state = await run_personas(selected_personas, video_part, app_name, user_id)
    result = await get_ux_lead_analysis(state, video_part, app_name, user_id)
    return result
