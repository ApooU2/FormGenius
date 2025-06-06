#!/usr/bin/env python3
"""
Test script for FormGenius batched API implementation using DemoQA practice form
"""

import asyncio
import json
import logging
import os
from formgenius.core.agent import FormGeniusAgent
from formgenius.core.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FormGenius-Test")

# DemoQA practice form URL
DEMOQA_URL = "https://demoqa.com/automation-practice-form"

async def main():
    # Initialize FormGenius agent
    logger.info("Initializing FormGenius agent")
    agent = FormGeniusAgent()
    
    # Log API service status
    logger.info(f"AI service available: {agent.data_generator.ai_service.is_available()}")
    
    # Test with DemoQA practice form
    logger.info(f"Testing FormGenius on DemoQA form: {DEMOQA_URL}")
    result = await agent.fill_form(DEMOQA_URL)
    
    # Save results to file
    output_file = "demoqa_test_results.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    # Print API usage metrics
    if "api_usage" in result:
        logger.info("API Usage Metrics:")
        for key, value in result["api_usage"].items():
            logger.info(f"  {key}: {value}")
    else:
        logger.warning("No API usage metrics found in results. AI service may not be available.")
    
    logger.info(f"Test completed. Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
