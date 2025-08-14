# Python Code Execution API

API to execute Python code and return results.

## Usage

**POST** `/execute`

```json
{
  "code": "print('Hello, World!')",
  "timeout": 30
}
```

**Response:**
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": "",
  "execution_time": 0.045
}
```

## Deploy on Railway

1. Push to GitHub
2. Connect Railway to your repo
3. Railway will detect the Dockerfile and deploy automatically
