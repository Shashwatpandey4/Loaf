# Loaf UI Integration

The UI has been connected to the backend functionality from `scripts/demo.py`.

## How to Run

### Start Both Servers

Run the single script to start both the API server and UI server:

```bash
./run.sh
```

This will start:
- **API Server** on `http://localhost:8000`
- **UI Server** on `http://localhost:8080`

Then open `http://localhost:8080` in your browser.

**Alternative:** If you want to run them separately:

```bash
# Terminal 1 - API Server
python api_server.py

# Terminal 2 - UI Server
cd UI
python -m http.server 8080
```

### 3. Use the Chat Interface

1. Enter your meal plan request in the input field (e.g., "Create a 7-day vegetarian meal plan")
2. The UI will call the API and display the generated meal plan
3. The meal plan will be processed and saved automatically

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health check
- `POST /chat` - Process a chat message and return a meal plan
  - Request body: `{"message": "your message", "run_workflow": false}`
  - Response: `{"meal_plan": {...}, "message": "...", "success": true}`

## Configuration

The API base URL is configured in `UI/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change this if your server is running on a different host/port.

## Notes

- The API server wraps the functionality from `scripts/demo.py` without modifying it
- The meal plan is automatically processed and saved (via `test_mock_meal_plan`)
- Set `run_workflow: true` in the API request to also run the full weekly meal workflow (grocery list, calendar events, payment, etc.)

