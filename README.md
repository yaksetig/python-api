# Python Code Execution API

Asynchronous API to execute Python code and return results.

## Usage

### Start Code Execution
**POST** `/run`

```json
{
  "code": "print('Hello, World!')"
}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "message": "Code execution started. Use /status/{job_id} to check progress."
}
```

### Check Execution Status
**GET** `/status/{job_id}`

**Response (Running):**
```json
{
  "status": "executing",
  "started_at": "2024-01-15T10:30:00.123456"
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "success": true,
  "output": "Hello, World!\n",
  "error": "",
  "execution_time": 0.045,
  "started_at": "2024-01-15T10:30:00.123456",
  "completed_at": "2024-01-15T10:30:00.168456"
}
```

**Response (Failed):**
```json
{
  "status": "failed",
  "success": false,
  "output": "",
  "error": "ZeroDivisionError: division by zero",
  "execution_time": 0.012,
  "started_at": "2024-01-15T10:30:00.123456",
  "completed_at": "2024-01-15T10:30:00.135456"
}
```

## Deploy on Railway

1. Push to GitHub
2. Connect Railway to your repo
3. Railway will detect the Dockerfile and deploy automatically
