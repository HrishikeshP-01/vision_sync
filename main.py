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

load_dotenv()


async def run_personas(app_name: str, user_id: str, video_part):
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
    with open('personas.json', 'r') as f:
        personas = json.load(f)

    for persona in personas:

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

    pprint(user_surveys)
    with open('user_survey.json', 'w', encoding='utf-8') as f:
        json.dump(user_surveys, f, indent=4)

if __name__ == "__main__":

    with open('Demo.mp4', 'rb') as f:
        video_bytes = f.read()
    video_part = types.Part(
        inline_data=types.Blob(
            mime_type='video/mp4',
            data=video_bytes
        )
    )

    asyncio.run(run_personas(
        app_name='X',
        user_id='Y',
        video_part=video_part
    ))
