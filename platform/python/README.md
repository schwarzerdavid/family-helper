# Python Platform Wrapper

Platform abstraction layer for Python services in the Family Helper ecosystem.

## Role

Provides consistent interfaces for infrastructure services used by Python-based microservices (User Profiles, Files & Documents).

## Key Interfaces

```python
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def info(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None: ...
    
    @abstractmethod
    def error(self, msg: str, meta: Optional[Dict[str, Any]] = None) -> None: ...

class Config(ABC):
    @abstractmethod
    def get(self, key: str, required: bool = True, default: Any = None) -> Any: ...

class Db(ABC):
    @abstractmethod
    async def query(self, sql: str, params: Optional[List] = None) -> List[Dict]: ...
    
    @abstractmethod
    async def query_one(self, sql: str, params: Optional[List] = None) -> Dict: ...

class ObjectStorage(ABC):
    @abstractmethod
    async def put(self, key: str, content: bytes, content_type: str) -> Dict[str, str]: ...
    
    @abstractmethod
    async def presign_put(self, key: str, expires_sec: int) -> str: ...
```

## Usage

1. Install the platform wrapper:
   ```bash
   pip install family-helper-platform-py
   ```

2. Use in FastAPI services:
   ```python
   from platform_py import db, storage, pubsub, log
   from fastapi import APIRouter, UploadFile
   
   router = APIRouter()
   
   @router.post("/files")
   async def upload(file: UploadFile):
       key = f"files/{file.filename}"
       content = await file.read()
       await storage.put(key, content, file.content_type or "application/octet-stream")
       
       row = await db.query_one(
           "insert into files (key, name, content_type) values ($1,$2,$3) returning id",
           [key, file.filename, file.content_type]
       )
       
       await pubsub.publish("FileUploaded:v1", {"fileId": row["id"], "key": key})
       log.info("file.uploaded", {"file_id": row["id"], "key": key})
       return {"id": row["id"], "key": key}
   ```

## Implementation Notes

- Uses asyncio-compatible libraries (asyncpg, aioredis, aioboto3)
- Integrates with Pydantic for configuration validation
- Provides FastAPI middleware and dependency injection
- Supports structured logging with correlation IDs
- Includes health check endpoints