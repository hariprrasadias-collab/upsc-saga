from backend.app.services.model_manager import model_manager

print("🧪 Testing Models via ModelManager...")

models_to_test = [
    model_manager.PRO_MODELS[0],
    model_manager.FAST_MODELS[0]
]

for m in models_to_test:
    print(f"\nTargeting {m}...")
    try:
        resp = model_manager.generate_content("Ping", forced_model=m)
        print(f"✅ SUCCESS: {m} responded.")
    except Exception as e:
        print(f"❌ FAILED: {m} - {e}")
