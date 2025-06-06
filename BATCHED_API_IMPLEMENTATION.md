# FormGenius API Usage Optimization

## Overview

FormGenius has been updated to use batched API calls, significantly reducing the number of calls made to the Google Gemini API. This optimization helps stay within the rate limit of 15 calls per minute while maintaining all functionality.

## Key Improvements

1. **Batched API Calls**: Multiple field value generation requests are now consolidated into a single comprehensive API call.
   - Reduced API usage from ~13-18 calls per form to 1-2 calls per form
   - Improved response time by reducing the number of network requests

2. **Page Context Integration**: 
   - Credentials and instructions found on the page are now passed to the AI for better form filling
   - Batch requests include this context for more accurate field value generation

3. **API Usage Metrics**:
   - Added detailed tracking of API usage
   - Reports include metrics on call frequency, efficiency, and rate limits
   - Helps monitor API consumption to stay within limits

## How It Works

The batched implementation works by:

1. Detecting all form fields on a page
2. Analyzing the page for credentials and instructions
3. Constructing a single prompt that includes all fields and context
4. Making a single API call to generate values for all fields
5. Parsing the JSON response to map values to the appropriate fields

## Usage

No changes to the API are required. The batching happens automatically when you use:

```python
agent = FormGeniusAgent()
result = await agent.fill_form(url)
```

The response will now include API usage metrics:

```python
{
    "success": true,
    "url": "https://example.com/form",
    "forms_found": 1,
    "scenarios_executed": 1,
    "api_usage": {
        "total_api_calls": 2,
        "batch_calls": 1,
        "non_batch_calls": 1,
        "calls_last_minute": 2,
        "calls_last_five_minutes": 2,
        "average_call_duration": 0.85,
        "batch_efficiency": "1 batched calls replaced approximately 8 individual calls",
        "estimated_rate": "2 calls/minute"
    }
}
```

## Benefits

- **Rate Limit Compliance**: Stays within the 15 calls/minute rate limit
- **Improved Performance**: Faster form processing due to fewer network requests
- **Better Data Generation**: Context-aware data generation using page credentials and instructions
- **Detailed Metrics**: Track API usage to optimize further if needed

## Implementation Details

The core changes were made to:
- `ai_service.py`: Added batched API call implementation
- `data_generator.py`: Updated to use batched calls instead of individual field requests
- `agent.py`: Modified to pass page context to data generator and include API metrics in results
