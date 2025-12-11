from app.services.model_manager import model_manager

print(f"ModelManager Configured: {model_manager.is_configured}")

if model_manager.is_configured:
    try:
        response = model_manager.generate_content("Hello", model_type='fast')
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
