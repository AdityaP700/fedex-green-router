# Move API-related modules
Move-Item route_engine backend/app/api/
Move-Item security backend/app/api/

# Move core modules
Move-Item config backend/app/core/
Move-Item models backend/app/core/

# Move service modules
Move-Item data_collection backend/app/services/
Move-Item emissions backend/app/services/
Move-Item ml_layer backend/app/services/
Move-Item processing backend/app/services/
Move-Item preferences backend/app/services/

# Move database modules
Move-Item persistence backend/app/db/

# Move utility modules
Move-Item utils backend/app/utils/
Move-Item validation backend/app/utils/
Move-Item error_handling backend/app/utils/
Move-Item monitoring backend/app/utils/
Move-Item input_handler backend/app/utils/
Move-Item feedback backend/app/utils/

# Move test files
Move-Item tests backend/
Move-Item test_demo.py backend/tests/
Move-Item run_tests.py backend/tests/
Move-Item pytest.ini backend/

# Move main application files
Move-Item main.py backend/
Move-Item requirements.txt backend/
Move-Item pyproject.toml backend/
Move-Item .env backend/

# Clean up pycache
Remove-Item -Recurse -Force __pycache__/ -ErrorAction SilentlyContinue 