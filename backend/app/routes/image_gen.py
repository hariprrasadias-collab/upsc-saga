"""
Image Generation API Route
Uses Google Gemini API (Nano Banana) via REST for AI image generation.
Includes fallback model chain for reliability.
"""
from flask import Blueprint, request, jsonify
import requests as http_requests
import os
import base64

image_gen_bp = Blueprint('image_gen', __name__)

# Model fallback chain (try in order)
IMAGE_MODELS = [
    'gemini-2.5-flash-image',                # Nano Banana (production)
    'gemini-2.0-flash-exp-image-generation',  # Experimental
]


def try_gemini_image(api_key: str, prompt: str, model: str) -> dict:
    """Try generating an image with a specific Gemini model."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    response = http_requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 429:
        return {'error': 'quota_exceeded', 'model': model}
    
    if response.status_code != 200:
        return {'error': f'api_error_{response.status_code}', 'model': model}

    result = response.json()

    # Extract image from response
    if 'candidates' in result:
        for candidate in result['candidates']:
            if 'content' in candidate:
                for part in candidate['content'].get('parts', []):
                    if 'inlineData' in part:
                        image_data = part['inlineData']['data']
                        mime_type = part['inlineData'].get('mimeType', 'image/png')
                        data_url = f"data:{mime_type};base64,{image_data}"
                        return {'success': True, 'image_url': data_url, 'model': model}

    return {'error': 'no_image_in_response', 'model': model}


def try_openrouter_image(prompt: str) -> dict:
    """Try generating an image via OpenRouter's image-capable models."""
    or_key = os.environ.get('OPENROUTER_API_KEY')
    if not or_key:
        return {'error': 'no_openrouter_key'}
    
    try:
        # Use OpenRouter with a model that supports image generation
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {or_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/hariprrasadias/upsc-saga",
            "X-Title": "UPSC Second Brain"
        }
        
        payload = {
            "model": "google/gemini-2.5-flash-image:free",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "image"}
        }
        
        response = http_requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            result = response.json()
            # OpenRouter may return image data in the response
            choices = result.get('choices', [])
            if choices:
                content = choices[0].get('message', {}).get('content', '')
                # Check if it contains base64 image data
                if content and 'data:image' in content:
                    return {'success': True, 'image_url': content, 'model': 'openrouter'}
        
        return {'error': f'openrouter_failed_{response.status_code}'}
    except Exception as e:
        return {'error': str(e)}


@image_gen_bp.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate an image using Gemini's image generation capability via REST API."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Gemini API key not configured'}), 500

        # Sanitize prompt
        clean_prompt = prompt[:500].replace('\n', ' ').strip()
        image_prompt = f"Generate a detailed, high-quality educational illustration for: {clean_prompt}"

        # Try each model in the fallback chain
        all_errors = []
        for model in IMAGE_MODELS:
            result = try_gemini_image(api_key, image_prompt, model)
            if result.get('success'):
                result['prompt_used'] = clean_prompt
                return jsonify(result)
            all_errors.append(result)
            print(f"Image gen: {model} failed - {result.get('error')}")
        
        # Try OpenRouter as last resort
        or_result = try_openrouter_image(image_prompt)
        if or_result.get('success'):
            or_result['prompt_used'] = clean_prompt
            return jsonify(or_result)

        # All failed — check if it was quota
        quota_errors = [e for e in all_errors if e.get('error') == 'quota_exceeded']
        if quota_errors:
            return jsonify({
                'success': False,
                'error': 'Image generation quota exceeded. The free API limit has been reached. Please try again later or check your Gemini API billing.'
            }), 429
        
        return jsonify({
            'success': False,
            'error': f'All image models failed. Errors: {[e.get("error") for e in all_errors]}'
        }), 422

    except http_requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Image generation timed out. Try a simpler prompt.'}), 504
    except Exception as e:
        print(f"Image generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
