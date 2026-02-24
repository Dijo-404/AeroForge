# src/synthesis/multimodal_reporter.py
import os
import json
import logging

logger = logging.getLogger("Multimodal Reporter")

def generate_svg_heatmap(simulation_results: dict, output_path: str = "heatmap.svg"):
    """
    Mock for Gemini 3.1 Pro Code-Based SVG Heatmap Animation.
    Uses Layered Iteration technique for vector generation.
    """
    logger.info("Generating dynamic SVG heatmap from simulation metrics (Live Gemini Code Gen)...")
    
    max_disp = simulation_results.get("max_displacement_mm", 0)
    von_mises = simulation_results.get("von_mises_stress_MPa", 0)
    color = "green" if simulation_results.get("survived") else "red"
    
    try:
        from google import genai
        from google.genai import types
        from src.config import settings
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"Generate exclusively raw, unmarkdown-wrapped SVG code visualizing a mechanical component under {von_mises} MPa of stress, displacing {max_disp} mm. Make it look like a thermal {color} heatmap.",
            config=types.GenerateContentConfig(
                system_instruction="You are an expert dataviz engineer. Output ONLY raw SVG string code. No markdown fences, no explanations. Just raw <svg>...</svg>.",
                response_mime_type="text/plain",
            ),
        )
        svg_code = response.text.strip().removeprefix('```svg').removeprefix('```xml').removeprefix('```').removesuffix('```')
        
    except Exception as e:
        logger.warning(f"Failed to generate API SVG, falling back to mock: {e}")
        svg_code = f"""<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#1a1a1a" />
            <circle cx="200" cy="200" r="{min(200, max_disp * 10 + 50)}" fill="{color}" opacity="0.8">
                <animate attributeName="r" values="50;{min(200, max_disp * 10 + 50)};50" dur="2s" repeatCount="indefinite" />
            </circle>
            <text x="200" y="50" font-family="Arial" font-size="20" fill="white" text-anchor="middle">Stress Map: {von_mises} MPa</text>
        </svg>"""
    
    with open(output_path, "w") as f:
        f.write(svg_code)
        
    logger.info(f"SVG saved to {output_path}")
    return output_path

def generate_audio_briefing(session_state: dict, output_path: str = "briefing.mp3"):
    """
    Mock for Gemini TTS API via Chirp 3 HD models with MultiSpeakerVoiceConfig.
    """
    logger.info("Synthesizing multi-speaker auditory briefing using Chirp 3 HD...")
    
    # In reality, this would use google.genai or the cloud Text-to-Speech API
    #   client = google.cloud.texttospeech_v1.TextToSpeechClient()
    #   voice = texttospeech.VoiceSelectionParams(name="en-US-Journey-F", ...)
    
    # Create a mock text file instead to simulate the TTS transcript
    transcript_path = output_path.replace('.mp3', '.txt')
    
    transcript = f"""
    [Charon - Informative]: The target matrix selected was {session_state.get('final_formulation', {}).get('matrix')}. 
    [Sadaltager - Knowledgeable]: Simulation indicates max displacement at {session_state.get('simulation_results', {}).get('max_displacement_mm')} mm.
    """
    
    with open(transcript_path, "w") as f:
        f.write(transcript.strip())
        
    logger.info(f"Mock Audio Transcript saved to {transcript_path}")
    return transcript_path

def finalize_presentation(session_state: dict, output_dir: str = "./reports"):
    os.makedirs(output_dir, exist_ok=True)
    svg_file = os.path.join(output_dir, "heatmap_animation.svg")
    audio_file = os.path.join(output_dir, "executive_briefing.mp3")
    
    generate_svg_heatmap(session_state.get("simulation_results", {}), svg_file)
    generate_audio_briefing(session_state, audio_file)
    
    return svg_file, audio_file
