#!/usr/bin/env python3
"""Startup script for MD2Word API server"""

import uvicorn
from .config import settings

def main():
    """Main entry point for running the server"""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )

if __name__ == "__main__":
    main()