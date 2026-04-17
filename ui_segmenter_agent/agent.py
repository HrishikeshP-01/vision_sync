from google.adk.agents.llm_agent import Agent
from moviepy import *
import os

def extract_ui_screen(video_path: str, t: int, filename: str) -> None:
    """
    Saves the frame of clip corresponding to time t in filename. 
    t can be expressed in seconds
    Args:
        video_path (str): Path to the video
        t (int): Moment of the frame in seconds, to be saved.
        filename (str): File name of the image. Extension should be .png
    Returns:
        None: Doesn't return an output
    """
    buffer = 4
    clip = VideoFileClip(video_path)
    os.makedirs('output/segment', exist_ok=True)
    clip.save_frame(f'output/segment/{filename}', t=t+buffer)


ui_segmenter_agent = Agent(
    model='gemini-2.5-flash',
    name='ui_segmenter_agent',
    description='Agent that parses a UI walkthrough video & returns images of the various UI screens',
    instruction="""
    You parse UI walkthrought videos & returns images of UI screens
    Your approach:
        1. You analyze the video of UI walkthrough provided to you
        2. Use the extract_ui_screen tool to extract an image of a distinct UI screen
        3. DO NOT EXTRACT THE SAME SCREEN TWICE
        4. Use a filename that embodies the context of the UI Screen. IT SHOULD NOT BE MORE THAN 3 WORDS AND SOULD NOT HAVE SPACES
    Path to the video is: demo.mp4
    """,
    tools = [extract_ui_screen]
)

root_agent = ui_segmenter_agent