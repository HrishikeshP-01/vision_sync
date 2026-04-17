import os
import uuid
from dotenv import load_dotenv
from pprint import pprint
import asyncio
import json
import base64
from pathlib import Path

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from ui_segmenter_agent.agent import ui_segmenter_agent
from participant_pwd_agent.agent import participant_pwd_agent
from accessibility_ui_designer.agent import accessibility_ui_designer
from functions.accessibility_emulator import simulate_color_blindness

load_dotenv()

# Segment video into images
async def segment_images(video_part, app_name: str, user_id:str)->None:
    session_service = InMemorySessionService()
    initial_state = {
    }
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state
    )
    runner = Runner(
        agent=ui_segmenter_agent,
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
        continue

    return

# Generate Surveys
async def generate_surveys(conditions, app_name: str, user_id: str):
    survey_results = {}

    session_service = InMemorySessionService()
    
    for condition in conditions:
        folder = Path(f'output/segment')
        extensions = {'.png', '.jpg', '.jpeg'}
        for img_file in folder.iterdir():
            if img_file.suffix.lower() in extensions:
                simulate_color_blindness(img_file, condition, 'output')

        state = {
        "condition": condition
        }
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            state=state
        )
        runner = Runner(
            agent=participant_pwd_agent,
            app_name=app_name,
            session_service=session_service
        )

        image_parts = []
        folder = Path(f'output/{condition}')
        extensions = {'.png', '.jpg', '.jpeg'}
        for img_file in folder.iterdir():
            if img_file.suffix.lower() in extensions:
                with open(img_file, 'rb') as f:
                    img_bytes = f.read()
                mime_type = f"image/{img_file.suffix.lower().replace('.', '')}"
                if "jpg" in mime_type: 
                    mime_type = "image/jpeg"
                image_parts.append(
                    types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
                )

        content = types.Content(role='user', parts=image_parts)

        events = runner.run_async(
            user_id = session.user_id,
            session_id = session.id,
            new_message = content
        )

        async for event in events:
            if event.is_final_response():
                survey_results[condition] = event.content.parts[0].text

    pprint(survey_results)
    return survey_results

async def generate_ui_analysis(survey_results, app_name: str, user_id: str):
    session_service = InMemorySessionService()
    initial_state = {
        'company': f'{os.getenv("COMPANY")}',
        'user_surveys': survey_results
    }
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state
    )
    runner = Runner(
        agent=accessibility_ui_designer,
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
        if event.is_final_response():
            survey_results['UI Lead'] = event.content.parts[0].text
    pprint(survey_results)
    return survey_results

# Generate UI analysis
if __name__=="__main__":
    with open('demo.mp4', 'rb') as f:
        video_bytes = f.read()
    video_part = types.Part(
        inline_data=types.Blob(
            mime_type='video/mp4',
            data=video_bytes
        )
    )
    survey = asyncio.run(
        generate_surveys(['protanopia', 'tritanopia'], app_name='X', user_id='Y')
    )
    asyncio.run(
        generate_ui_analysis(survey, app_name='X', user_id='Y')
    )