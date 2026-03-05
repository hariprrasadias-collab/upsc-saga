import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app import create_app
from app.services.mock_test_service import MockTestService

app = create_app()
with app.app_context():
    print("Testing MockTestService...")
    res = MockTestService.generate_from_topic("NCERT Cl 6: Our Pasts I - Ch 1", 2)
    print("Result:", res)
