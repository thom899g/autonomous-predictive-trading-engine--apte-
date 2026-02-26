"""
Firebase Client Module
Manages all Firestore interactions for state persistence and real-time updates.
Implements proper error handling and connection pooling.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter

from apte_config import config

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Singleton Firebase client with connection management"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                # Initialize Firebase app if not already initialized
                if not firebase_admin._apps:
                    cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred, {
                        'projectId': config.FIREBASE_PROJECT_ID,
                    })
                    logger.info("Firebase app initialized successfully")
                
                self.db: FirestoreClient = firestore.client