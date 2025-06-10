#!/usr/bin/env python3
"""
Beta Verification Script for VlogForge Project

This script performs comprehensive verification of the VlogForge project's
environment, core components, and integration points. It generates detailed
reports and logs for beta testing purposes.
"""

import asyncio
import json
import logging
import os
import sys
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('beta_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BetaVerifier:
    """Main class for beta verification process."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "directories": {},
                "env_vars": {},
                "dependencies": {}
            },
            "core_components": {},
            "integration_points": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        self.project_root = Path(__file__).parent
        self.required_dirs = [
            "core",
            "api_intergrations",
            "tests",
            "ui",
            "data"
        ]
        self.required_env_vars = [
            "OPENAI_API_KEY",
            "YOUTUBE_API_KEY",
            "INSTAGRAM_API_KEY"
        ]

    async def verify_environment(self) -> None:
        """Verify environment setup and dependencies."""
        logger.info("Starting environment verification...")
        
        # Check Python version
        python_version = platform.python_version()
        self.results["environment"]["python_version"] = python_version
        logger.info(f"Python version: {python_version}")

        # Verify required directories
        for dir_name in self.required_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists()
            self.results["environment"]["directories"][dir_name] = exists
            if not exists:
                logger.warning(f"Required directory missing: {dir_name}")

        # Check environment variables
        for var in self.required_env_vars:
            value = os.getenv(var)
            self.results["environment"]["env_vars"][var] = bool(value)
            if not value:
                logger.warning(f"Required environment variable missing: {var}")

        # Verify dependencies
        try:
            import pkg_resources
            with open(self.project_root / "requirements.txt") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            installed = {pkg.key for pkg in pkg_resources.working_set}
            missing = [req for req in requirements if req.split("==")[0].lower() not in installed]
            
            self.results["environment"]["dependencies"] = {
                "total": len(requirements),
                "installed": len(requirements) - len(missing),
                "missing": missing
            }
            
            if missing:
                logger.warning(f"Missing dependencies: {', '.join(missing)}")
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")

    async def verify_core_components(self) -> None:
        """Verify core functionality modules."""
        logger.info("Starting core components verification...")
        
        core_modules = [
            "auto_posting",
            "hashtag_performance",
            "audience_tracker",
            "engagement_tracker",
            "social_media_analyzer",
            "pdf_report_generator",
            "lead_magnet",
            "idea_vault",
            "idea_integrator",
            "content_manager",
            "batch_content_generator",
            "a_b_testing",
            "referral_tracker",
            "engagement_heatmap",
            "ai_caption_suggester"
        ]

        for module in core_modules:
            try:
                module_path = self.project_root / "core" / f"{module}.py"
                if not module_path.exists():
                    logger.warning(f"Core module missing: {module}")
                    continue

                # Import and verify module
                import importlib.util
                spec = importlib.util.spec_from_file_location(module, module_path)
                if spec and spec.loader:
                    module_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_obj)
                    
                    # Basic functionality check
                    self.results["core_components"][module] = {
                        "status": "passed",
                        "methods": [name for name in dir(module_obj) if not name.startswith("_")]
                    }
                else:
                    raise ImportError(f"Could not load module: {module}")
                    
            except Exception as e:
                logger.error(f"Error verifying {module}: {str(e)}")
                self.results["core_components"][module] = {
                    "status": "failed",
                    "error": str(e)
                }

    async def verify_integration_points(self) -> None:
        """Verify external service connections and API integrations."""
        logger.info("Starting integration points verification...")
        
        # Check API integrations
        api_modules = [
            "youtube_api",
            "instagram_api",
            "twitter_api"
        ]

        for api in api_modules:
            try:
                module_path = self.project_root / "api_intergrations" / f"{api}.py"
                if not module_path.exists():
                    logger.warning(f"API integration missing: {api}")
                    continue

                # Import and verify API module
                import importlib.util
                spec = importlib.util.spec_from_file_location(api, module_path)
                if spec and spec.loader:
                    module_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_obj)
                    
                    # Basic API functionality check
                    self.results["integration_points"][api] = {
                        "status": "passed",
                        "methods": [name for name in dir(module_obj) if not name.startswith("_")]
                    }
                else:
                    raise ImportError(f"Could not load API module: {api}")
                    
            except Exception as e:
                logger.error(f"Error verifying {api}: {str(e)}")
                self.results["integration_points"][api] = {
                    "status": "failed",
                    "error": str(e)
                }

    def generate_report(self) -> None:
        """Generate verification report in JSON format."""
        logger.info("Generating verification report...")
        
        # Calculate summary statistics
        total_tests = (
            len(self.results["environment"].get("directories", {})) +
            len(self.results["environment"].get("env_vars", {})) +
            len(self.results["core_components"]) +
            len(self.results["integration_points"])
        )
        
        passed = sum(1 for comp in self.results["core_components"].values() if comp.get("status") == "passed")
        failed = sum(1 for comp in self.results["core_components"].values() if comp.get("status") == "failed")
        warnings = len([v for v in self.results["environment"].values() if isinstance(v, dict) and not all(v.values())])
        
        self.results["summary"].update({
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        })
        
        # Save report
        report_path = self.project_root / "beta_verification_report.json"
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Verification report saved to: {report_path}")

    async def run_verification(self) -> None:
        """Run all verification steps."""
        try:
            await self.verify_environment()
            await self.verify_core_components()
            await self.verify_integration_points()
            self.generate_report()
            
            # Print summary
            summary = self.results["summary"]
            logger.info("\nVerification Summary:")
            logger.info(f"Total Tests: {summary['total_tests']}")
            logger.info(f"Passed: {summary['passed']}")
            logger.info(f"Failed: {summary['failed']}")
            logger.info(f"Warnings: {summary['warnings']}")
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            sys.exit(1)

def main():
    """Main entry point for the verification script."""
    verifier = BetaVerifier()
    asyncio.run(verifier.run_verification())

if __name__ == "__main__":
    main() 