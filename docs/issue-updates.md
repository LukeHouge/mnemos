# Mnemos Issue Updates & Execution Plan

> **How to use this document**: Copy-paste each section into the corresponding GitHub issue.
> New issues have full bodies ready to paste into `gh issue create`.
> The execution roadmap at the bottom should be created as its own tracking issue.

---

## Housekeeping

### Close #19 (test)
Empty test issue with no content. Close it.

---

## Status Updates

### #14 — Tag CRUD (DONE)
**Status**: Implemented on branch `cursor/next-logical-issue-8b7c` (PR #30).

All acceptance criteria met:
- [x] All 5 CRUD endpoints working (`POST/GET/GET/{id}/PATCH/DELETE` on `/api/v1/tags`)
- [x] Tag name uniqueness enforced (409 Conflict)
- [x] Color field validates as hex color (#RRGGBB) or null
- [x] Unit tests for models (19), service (16), and routes (15) — 50 new tests
- [x] `just harness` passes cleanly (89 total tests)

### #12 — Document CRUD (PR Open)
**Status**: PR #29 open on branch `cursor/document-crud-functionality-351e`. Review and merge.

---

## Updated Issue Bodies

Each section below is the **complete replacement body** for the corresponding issue.

---

### #13 — User CRUD: Pydantic schemas, service, and routes

```markdown
## Summary

The `User` SQLAlchemy ORM model exists (`backend/app/db/models.py`) with an Alembic migration, but there are no Pydantic request/response schemas, no service layer, and no API routes for user management.

## What to Build

### 1. Pydantic Schemas (`app/models/user.py`)
- `UserCreate` — request model (email, display_name)
  - Email validated with Pydantic `EmailStr` (add `pydantic[email]` to deps)
  - display_name: 1–255 chars, whitespace-stripped (same pattern as TagCreate)
- `UserUpdate` — request model (email?, display_name?) — all fields optional
- `UserResponse` — response model (id, email, display_name, created_at, updated_at)
  - Use `model_config = {"from_attributes": True}` for ORM compatibility
- `UserListResponse` — paginated list (items, total, limit, offset)

### 2. User Service (`app/services/user_service.py`)
- `create_user(data: UserCreate) -> User` — insert new user, enforce unique email
- `get_user(user_id: UUID) -> User | None` — fetch by ID
- `get_user_by_email(email: str) -> User | None` — fetch by email (used by auth later)
- `list_users(limit, offset) -> tuple[list[User], int]` — list with pagination
- `update_user(user_id, data: UserUpdate) -> User | None` — partial update
- `delete_user(user_id) -> bool` — delete user (cascade deletes documents per ORM config)
- Uses async SQLAlchemy session via `Depends(get_session)` from `app/db/base.py`
- **Logging**: Use `user_id` and `user_email` as extra keys (avoid `name` — it's reserved in LogRecord)

### 3. API Routes (`app/routes/users.py`)
- `POST /api/v1/users` — create user (201 Created)
- `GET /api/v1/users` — list users (paginated with `limit` and `offset` query params)
- `GET /api/v1/users/{id}` — get single user (404 if not found)
- `PATCH /api/v1/users/{id}` — update user (409 on email conflict)
- `DELETE /api/v1/users/{id}` — delete user (204 No Content)
- Register router in `app/main.py`
- Use `get_user_service` dependency pattern (same as `get_tag_service` in tags.py)

### 4. Tests (`tests/unit/test_user_*.py`)
- `test_user_models.py` — Model validation tests:
  - Valid email formats, invalid email formats
  - display_name length limits, whitespace stripping
  - UserUpdate with no fields, partial fields
  - UserListResponse with items and empty
- `test_user_service.py` — Service tests with mocked DB session:
  - CRUD happy paths
  - Duplicate email → IntegrityError
  - Not found → None / False
  - Update with no fields → returns unchanged
- `test_user_routes.py` — Route tests with mocked service:
  - All 5 endpoints: success, validation errors, not found, conflicts
  - Invalid UUID → 422

## Implementation Notes
- Follow the exact same patterns as Tag CRUD (PR #30 / branch `cursor/next-logical-issue-8b7c`)
- The `get_user_by_email` method is critical — #23 (Auth) will depend on it
- Do NOT add password fields here — that belongs in #23 (Auth) which will extend the User model

## Error Responses
| Scenario | Status | Detail |
|---|---|---|
| Duplicate email | 409 | "A user with this email already exists" |
| User not found | 404 | "User not found" |
| Invalid input | 422 | Pydantic validation errors |
| Invalid UUID | 422 | Path parameter validation |

## Architecture Rules
- Follow the layered architecture: Routes → Services → Models
- Use `Depends()` for service injection in routes
- Async-first: all handlers and service methods must be async
- Handle unique constraint violations gracefully (409 Conflict)
- Run `just harness` before committing

## Acceptance Criteria
- [ ] All 5 CRUD endpoints working
- [ ] Email validated as proper email format
- [ ] Email uniqueness enforced at service layer (409 on conflict)
- [ ] Pydantic validation on all inputs
- [ ] Pagination support on list endpoint
- [ ] Unit tests for models, service, and routes (~40+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
None — this can start immediately. The ORM model and migration already exist.

## Effort Estimate
Small-medium (~2–3 hours). Very similar to Tag CRUD which is already done.

## Parallel-Safe
Yes — no conflicts with Document CRUD or Tag CRUD issues.
```

---

### #15 — Document-Tag association API

```markdown
## Summary

The `DocumentTag` many-to-many association table exists in the ORM and migration, but there is no API to manage the relationship between documents and tags.

## What to Build

### 1. Pydantic Schemas (`app/models/document_tag.py`)
- `DocumentTagRequest` — request model: `tag_id: UUID`
- `DocumentTagBulkRequest` — request model: `tag_ids: list[UUID]` (add multiple tags at once)
- `DocumentTagsResponse` — list of TagResponse items for a document
- `TagDocumentsResponse` — paginated list of DocumentResponse items for a tag

### 2. Document-Tag Service (`app/services/document_tag_service.py`)
- `add_tag_to_document(document_id, tag_id)` — associate a tag (idempotent: no error if already associated)
- `add_tags_to_document(document_id, tag_ids)` — bulk associate
- `remove_tag_from_document(document_id, tag_id)` — remove association
- `get_document_tags(document_id)` — list tags for a document
- `get_documents_by_tag(tag_id, limit, offset)` — list documents with a given tag (paginated)
- Validate both document and tag exist before operating (404 if either missing)

### 3. API Routes
Add to `app/routes/documents.py` (or new `app/routes/document_tags.py`):
- `POST /api/v1/documents/{id}/tags` — add tag(s) to document (accepts single tag_id or list)
- `DELETE /api/v1/documents/{id}/tags/{tag_id}` — remove tag from document
- `GET /api/v1/documents/{id}/tags` — list tags for a document

Add to `app/routes/tags.py`:
- `GET /api/v1/tags/{id}/documents` — list documents with this tag (paginated)

### 4. Tests
- Service tests for add/remove/list operations
- Route tests for all 4 endpoints
- Edge cases:
  - Duplicate association (idempotent — no error)
  - Non-existent document → 404
  - Non-existent tag → 404
  - Remove non-existent association → 404
  - Bulk add with mix of valid/invalid tag IDs

## Error Responses
| Scenario | Status | Detail |
|---|---|---|
| Document not found | 404 | "Document not found" |
| Tag not found | 404 | "Tag not found" |
| Association not found (on remove) | 404 | "Tag is not associated with this document" |

## Architecture Rules
- Follow the layered architecture: Routes → Services → Models
- Use `Depends()` for service injection in routes
- Async-first: all handlers and service methods must be async
- Run `just harness` before committing

## Acceptance Criteria
- [ ] Can add and remove tags from documents
- [ ] Can query tags for a document and documents for a tag
- [ ] Proper 404 handling for non-existent resources
- [ ] Idempotent tag addition (no duplicate errors)
- [ ] Pagination on "documents by tag" endpoint
- [ ] Bulk tag addition support
- [ ] Unit tests pass (~20+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #12 (Document CRUD) — needs Document service and routes
- **Hard dependency** on #14 (Tag CRUD) — needs Tag service and routes
- Both #12 and #14 have PRs open. Merge them first.

## Effort Estimate
Small (~2 hours). Straightforward association CRUD.

## Parallel-Safe
**Must start after** Document CRUD (#12) and Tag CRUD (#14) are merged — extends their route and service files.
```

---

### #17 — File upload and storage service

```markdown
## Summary

The Document model has `filename`, `file_path`, `file_size_bytes`, and `mime_type` fields, but there is no file upload handling or storage service. Users need to be able to upload PDFs, images, and other document files.

## What to Build

### 1. Storage Service (`app/services/storage_service.py`)
- `save_file(file: UploadFile, owner_id: UUID) -> FileInfo` — returns dataclass with file_path, file_size, mime_type, original_filename
- `get_file(file_path: str) -> Path` — returns resolved file path (validates it exists)
- `delete_file(file_path: str) -> bool` — removes file from storage
- Structure: `{UPLOAD_DIR}/{owner_id}/{uuid}_{sanitized_filename}`
- **Filename sanitization**: strip path traversal (`../`), limit length, replace special chars
- **Mime type validation**: allow list (PDF, PNG, JPG, JPEG, TIFF, WEBP)
- **File size validation**: configurable max, reject before writing to disk using `Content-Length` header + streaming size check
- **Atomic writes**: write to temp file, rename on success → no partial files on failure
- Run file I/O via `asyncio.to_thread` (non-blocking)

### 2. Config Updates (`app/config.py`)
- `UPLOAD_DIR: str = "./uploads"` — local storage directory
- `MAX_FILE_SIZE_MB: int = 50` — maximum upload size
- `ALLOWED_MIME_TYPES: str = "application/pdf,image/png,image/jpeg,image/tiff,image/webp"` — comma-separated
- Add `allowed_mime_types_list` property (same pattern as `cors_origins_list`)

### 3. Upload Route (`app/routes/documents.py`)
- `POST /api/v1/documents/upload` — multipart file upload
  - Accept `file: UploadFile` + form fields: `title`, `description` (optional), `owner_id`
  - Save file via storage service
  - Create Document record via document service
  - **On document creation failure**: clean up uploaded file (rollback)
  - Return DocumentResponse with file info (201 Created)
- `GET /api/v1/documents/{id}/download` — stream file download
  - Return `FileResponse` or `StreamingResponse` with correct `Content-Type` and `Content-Disposition`
  - 404 if document or file not found

### 4. Security Considerations
- Never expose internal file paths in API responses (use document ID + download URL)
- Validate mime type from file content (not just extension) — use `python-magic` or file header inspection
- Reject files with suspicious extensions (`.exe`, `.sh`, `.bat`, etc.)
- Ensure upload directory is outside the application root
- Add `.gitignore` entry for `uploads/` directory

### 5. Tests
- Storage service tests (mock filesystem with `tmp_path` fixture):
  - Save, retrieve, delete files
  - Filename sanitization (path traversal, special chars, long names)
  - Mime type rejection
  - File size rejection
  - Atomic write (cleanup on failure)
- Upload route tests (mock storage + document service):
  - Successful upload → 201
  - Invalid mime type → 415 Unsupported Media Type
  - File too large → 413 Request Entity Too Large
  - Missing file → 422
  - Document creation failure → file cleanup
- Download route tests:
  - Successful download with correct headers
  - File not found → 404

## Error Responses
| Scenario | Status | Detail |
|---|---|---|
| Invalid mime type | 415 | "Unsupported file type. Allowed: PDF, PNG, JPG, TIFF, WEBP" |
| File too large | 413 | "File exceeds maximum size of {MAX_FILE_SIZE_MB}MB" |
| Document not found | 404 | "Document not found" |
| File missing on disk | 404 | "File not found" |

## Architecture Rules
- Storage service is a new service — follows service layer rules
- Route delegates to storage service + document service
- No file path exposure in API responses
- Run `just harness` before committing

## Acceptance Criteria
- [ ] File upload endpoint accepts multipart form data
- [ ] Files saved to local filesystem with organized structure (`owner_id/uuid_filename`)
- [ ] Atomic writes — no partial files on failure
- [ ] Filename sanitization (path traversal prevention)
- [ ] File download/streaming endpoint works with correct headers
- [ ] Mime type validation (reject unsupported types)
- [ ] File size validation (reject before fully reading)
- [ ] Cleanup on failed document creation
- [ ] Upload directory not exposed in responses
- [ ] Unit tests pass (~25+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #12 (Document CRUD) — needs document service to create DB records
- Merge Document CRUD first.

## Effort Estimate
Medium (~3–4 hours). File I/O, security validation, error recovery.

## Parallel-Safe
Best started after Document CRUD (#12) is merged to avoid conflicts in `app/routes/documents.py`.
```

---

### #18 — PDF text extraction service

```markdown
## Summary

The Document ORM model has an `extracted_text` field, but there is no service to extract text from uploaded PDFs and other documents. Text extraction is a prerequisite for search and RAG functionality.

## What to Build

### 1. Extraction Service (`app/services/extraction_service.py`)
- `extract_text(file_path: str, mime_type: str) -> str` — returns extracted text string
- **PDF extraction** using `pymupdf` (PyMuPDF):
  - Extract text page-by-page
  - Preserve paragraph structure (join with double newlines)
  - Handle encrypted PDFs (log warning, return empty string)
- **Image OCR** (stretch goal for v2):
  - `pytesseract` for scanned PDFs and images
  - Detect if PDF is image-based (no extractable text) and fall back to OCR
  - Requires Tesseract system dependency — document in setup
- Handle extraction failures gracefully:
  - Corrupted files → return empty string + log error
  - Unsupported formats → return empty string + log warning
  - Never raise — callers should not fail because extraction failed
- **Run CPU-bound extraction in thread pool** via `asyncio.to_thread()` — non-blocking
- **Text cleanup**: strip excessive whitespace, normalize Unicode, limit max length (configurable)

### 2. Integration with Document Upload
- After file upload (#17), trigger text extraction automatically
- Update Document record's `extracted_text` field
- Extraction happens synchronously during upload for now (v1)
- **Future**: move to background job (#TBD Background Jobs issue) for better UX on large files

### 3. Standalone Re-extraction Endpoint
- `POST /api/v1/documents/{id}/extract` — manually trigger re-extraction
  - Useful after extraction logic improvements
  - Returns updated DocumentResponse with extracted_text populated
  - 404 if document not found

### 4. Dependencies to Add
- `pymupdf` (PyMuPDF) — PDF text extraction (MIT license, pure Python wheels available)
- Add to `pyproject.toml` dependencies

### 5. Config Updates (`app/config.py`)
- `MAX_EXTRACTED_TEXT_LENGTH: int = 500000` — max characters to store (safety limit)

### 6. Tests
- Extraction service tests:
  - PDF with text → extracts correctly (use a small test fixture PDF)
  - Empty PDF → returns empty string
  - Corrupted file → returns empty string (no exception)
  - Image file → returns empty string (OCR not yet implemented)
  - Long text → truncated to max length
  - Thread pool execution (verify `asyncio.to_thread` is used)
- Route tests for re-extraction endpoint:
  - Success → returns document with extracted_text
  - Document not found → 404
  - File missing on disk → appropriate error

### 7. Test Fixtures
- Create `tests/fixtures/` directory
- Add a small test PDF (1-2 pages with known text content)
- Add an empty PDF
- Keep fixtures small (< 50KB total)

## Architecture Rules
- Extraction service is a new service — follows service layer rules
- CPU-bound work runs in thread pool (never block the event loop)
- Graceful degradation: extraction failure must not prevent document upload
- Run `just harness` before committing

## Acceptance Criteria
- [ ] PDF text extraction works for standard text-based PDFs
- [ ] Extracted text stored in `Document.extracted_text`
- [ ] CPU-bound work runs in thread pool (`asyncio.to_thread`)
- [ ] Graceful handling of corrupted/unreadable files (no exceptions, empty string)
- [ ] Text cleanup (whitespace normalization, length limit)
- [ ] Re-extraction endpoint works
- [ ] Unit tests with test fixture PDFs
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #17 (File Upload) — needs files on disk to extract from
- **Hard dependency** on #12 (Document CRUD) — needs document service to update records

## Effort Estimate
Medium (~3 hours). PDF library integration, error handling, test fixtures.

## Parallel-Safe
Yes — creates new files only. No conflicts with other issues.
```

---

### #20 — Vector embeddings and Qdrant integration

```markdown
## Summary

Mnemos is a RAG (Retrieval-Augmented Generation) system, but currently has no vector storage or embedding capability. This issue adds the embedding pipeline and Qdrant vector database integration needed for semantic search.

## What to Build

### 1. Qdrant Infrastructure
- Add Qdrant service to `docker-compose.yml`:
  ```yaml
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
  ```
- Config settings in `app/config.py`:
  - `QDRANT_HOST: str = "qdrant"`
  - `QDRANT_PORT: int = 6333`
  - `QDRANT_COLLECTION: str = "mnemos_documents"`
  - `EMBEDDING_MODEL: str = "text-embedding-3-small"`
  - `EMBEDDING_DIMENSIONS: int = 1536`
  - `CHUNK_SIZE: int = 500` (tokens)
  - `CHUNK_OVERLAP: int = 50` (tokens)
- Health check integration: resolve the TODO in `app/routes/health.py` line 58

### 2. Embedding Service (`app/services/embedding_service.py`)
- `generate_embedding(text: str) -> list[float]` — embed a single text string
  - Uses OpenAI `text-embedding-3-small` (or configurable model)
  - Returns vector of `EMBEDDING_DIMENSIONS` floats
- `embed_chunks(chunks: list[str]) -> list[list[float]]` — batch embedding
  - Use OpenAI batch embedding API for efficiency
  - Handle rate limits with exponential backoff
- `chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]` — intelligent text chunking
  - **Strategy**: split on sentence boundaries, then group into chunks of ~`chunk_size` tokens
  - Overlap between chunks for context continuity
  - Handle very short texts (single chunk)
  - Handle empty text (return empty list)
  - Pure function — easy to unit test

### 3. Vector Store Service (`app/services/vector_service.py`)
- `initialize_collection()` — create Qdrant collection if it doesn't exist (called on startup)
- `upsert_document(document_id: UUID, chunks: list[str], vectors: list[list[float]])` — store embeddings with metadata:
  - Payload: `document_id`, `chunk_index`, `chunk_text`, `document_title`
  - Point IDs: deterministic from `document_id + chunk_index` for idempotent upserts
- `search(query_vector: list[float], limit: int, filters: dict | None) -> list[SearchHit]`
  - Returns list of (document_id, chunk_text, score, chunk_index)
  - Support Qdrant filters: by document_id, owner_id
- `delete_document(document_id: UUID)` — remove all vectors for a document
- `collection_info() -> dict` — return collection stats (point count, etc.) for health checks

### 4. Embedding Pipeline Integration
- After text extraction (#18), automatically generate embeddings and store in Qdrant
- Add method: `embed_and_store_document(document_id)` that orchestrates: fetch doc → chunk → embed → upsert
- `POST /api/v1/documents/{id}/embed` — manually trigger re-embedding
- `DELETE` a document should also remove its vectors from Qdrant

### 5. Batch Reprocessing
- `POST /api/v1/documents/embed-all` — re-embed all documents (admin operation)
  - Useful after changing embedding model or chunk size
  - Process in batches to avoid memory issues
  - Return count of processed documents

### 6. Dependencies to Add
- `qdrant-client>=1.7.0` — Qdrant Python client (async support)
- Add to `pyproject.toml` dependencies

### 7. Tests
- **Chunking logic tests** (pure unit tests — no mocking needed):
  - Short text → single chunk
  - Long text → multiple chunks with overlap
  - Empty text → empty list
  - Sentence boundary splitting
- **Embedding service tests** (mock OpenAI embeddings API):
  - Single embedding generation
  - Batch embedding
  - API error handling
- **Vector service tests** (mock Qdrant client):
  - Upsert, search, delete operations
  - Collection initialization
  - Filter application
- **Health check test**: verify Qdrant status reported

## Cost Considerations
- `text-embedding-3-small`: ~$0.02 per 1M tokens — very affordable
- A 10-page PDF ≈ 5,000 tokens ≈ $0.0001 per document
- Batch API calls are more efficient than individual calls
- Consider caching embeddings to avoid re-computation

## Architecture Rules
- Embedding service wraps OpenAI API — follows service layer rules
- Vector service wraps Qdrant client — follows service layer rules
- Chunking is a pure function — easily testable
- Run `just harness` before committing

## Acceptance Criteria
- [ ] Qdrant running in Docker Compose with health check
- [ ] Text chunking with configurable size and overlap
- [ ] Documents chunked and embedded after text extraction
- [ ] Vectors stored in Qdrant with document_id metadata
- [ ] Vector search returns relevant chunks with scores
- [ ] Document deletion removes vectors from Qdrant
- [ ] Health check reports Qdrant status
- [ ] Batch re-embedding endpoint
- [ ] Unit tests with mocked external services (~25+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #18 (PDF Text Extraction) — needs extracted text to embed
- Uses existing OpenAI service config for API key

## Effort Estimate
Large (~5–6 hours). New infrastructure (Qdrant), chunking algorithm, two new services.

## Parallel-Safe
Mostly yes — creates new files. Only shared edits: `docker-compose.yml` (Qdrant service), `config.py` (new settings), `health.py` (Qdrant health).
```

---

### #21 — Document search API (full-text + semantic)

```markdown
## Summary

A document management system needs robust search. This issue implements both full-text search (PostgreSQL) and semantic search (Qdrant vectors), with a unified search API.

## What to Build

### 1. Pydantic Schemas (`app/models/search.py`)
- `SearchRequest`:
  - `query: str` — search query (min 1 char)
  - `search_type: Literal["fulltext", "semantic", "hybrid"] = "hybrid"` — search mode
  - `filters: SearchFilters | None` — optional filters
  - `limit: int = 20` (1–100)
  - `offset: int = 0`
- `SearchFilters`:
  - `owner_id: UUID | None`
  - `tag_ids: list[UUID] | None`
  - `mime_type: str | None`
  - `created_after: datetime | None`
  - `created_before: datetime | None`
- `SearchResult`:
  - `document_id: UUID`
  - `title: str`
  - `snippet: str` — relevant text excerpt (150–300 chars) with match highlighted
  - `relevance_score: float` — 0.0–1.0 normalized score
  - `matched_chunk: str | None` — the chunk that matched (semantic only)
  - `match_type: Literal["fulltext", "semantic"]` — which search found this result
- `SearchResponse`:
  - `items: list[SearchResult]`
  - `total: int`
  - `query: str`
  - `search_type: str`
  - `took_ms: float` — search duration in milliseconds

### 2. Search Service (`app/services/search_service.py`)
- `fulltext_search(query, filters, limit, offset) -> list[SearchResult]`
  - PostgreSQL `to_tsvector` / `to_tsquery` on `extracted_text` + `title`
  - Rank results with `ts_rank_cd`
  - Fallback: `ILIKE` search if `tsvector` not configured
  - Generate snippets with `ts_headline` for highlighted excerpts
- `semantic_search(query, filters, limit, offset) -> list[SearchResult]`
  - Embed query text → Qdrant vector search → return matches
  - Apply filters via Qdrant filter conditions
  - Use chunk text as snippet
- `hybrid_search(query, filters, limit, offset) -> list[SearchResult]`
  - Run fulltext + semantic in parallel (`asyncio.gather`)
  - **Reciprocal Rank Fusion (RRF)** to combine results:
    - Score = sum(1 / (k + rank)) for each result across both lists
    - k = 60 (standard constant)
  - Deduplicate by document_id (keep highest combined score)
  - Re-sort by fused score
- `generate_snippet(text: str, query: str, max_length: int = 250) -> str`
  - Find query terms in text, extract surrounding context
  - Truncate cleanly at word boundaries

### 3. Database Enhancement
- Add PostgreSQL GIN index on `documents.title` and `documents.extracted_text`
- Create Alembic migration:
  ```sql
  CREATE INDEX idx_documents_title_search ON documents USING GIN (to_tsvector('english', title));
  CREATE INDEX idx_documents_text_search ON documents USING GIN (to_tsvector('english', extracted_text));
  ```
- Consider adding a materialized `tsvector` column for performance at scale

### 4. API Routes (`app/routes/search.py`)
- `POST /api/v1/search` — unified search endpoint (POST because of complex filter body)
- Register router in `app/main.py`

### 5. Tests
- **Search service tests** (mocked DB + vector store):
  - Fulltext search with results
  - Semantic search with results
  - Hybrid search with deduplication and rank fusion
  - Empty results
  - Filter application (by owner, tags, date range)
- **Snippet generation tests** (pure unit tests):
  - Query term found → highlighted excerpt
  - Query term not found → first N characters
  - Short text → return full text
- **Route tests**:
  - Valid search → 200 with results
  - Empty query → 422
  - Each search type works

## Performance Notes
- Hybrid search runs fulltext + semantic in parallel — latency is max(fulltext, semantic), not sum
- PostgreSQL GIN indexes make fulltext search fast even on large text columns
- Qdrant search is already indexed — typically < 50ms for reasonable collection sizes
- Consider caching frequent queries (stretch goal)

## Architecture Rules
- Search service is a new service — follows service layer rules
- Use `asyncio.gather` for parallel search execution
- Run `just harness` before committing

## Acceptance Criteria
- [ ] Full-text search across document titles and extracted text
- [ ] Semantic search via Qdrant vector similarity
- [ ] Hybrid search with Reciprocal Rank Fusion
- [ ] Result snippets with relevant text excerpts
- [ ] Filtering by owner, tags, mime type, date range
- [ ] Pagination on results
- [ ] Search duration reported in response
- [ ] GIN indexes created via Alembic migration
- [ ] Unit tests pass (~20+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #12 (Document CRUD) — needs documents in DB
- **Hard dependency** on #20 (Vector Embeddings) — needs Qdrant for semantic search
- Full-text search portion **can be developed first** without Qdrant

## Effort Estimate
Large (~5–6 hours). Multiple search strategies, rank fusion, database migration.

## Parallel-Safe
Yes — creates new files (`search.py` in models, services, routes). Only shared edit: `main.py` (register router).
```

---

### #22 — RAG-powered document chat

```markdown
## Summary

The current `/api/v1/ai/chat` endpoint is a simple proxy to OpenAI with no document context. The core value of Mnemos is RAG — answering questions using the user's own documents. This issue transforms the chat into a document-aware assistant.

## What to Build

### 1. Updated Pydantic Schemas (`app/models/ai.py`)
- Extend `ChatRequest` with optional fields:
  - `document_ids: list[UUID] | None = None` — scope chat to specific documents
  - `use_rag: bool = True` — enable/disable RAG context
  - `conversation_id: UUID | None = None` — for conversation continuity (stretch)
- Add `ChatSource` model:
  - `document_id: UUID`
  - `title: str`
  - `chunk_text: str` — the retrieved context chunk
  - `relevance_score: float`
- Extend `ChatResponse` with:
  - `sources: list[ChatSource] | None` — documents used to generate the answer

### 2. RAG Chat Service (`app/services/rag_service.py`)
- `rag_chat(message, document_ids, owner_id) -> RagResult`:
  1. **Embed** the user's question via embedding service
  2. **Search** Qdrant for top-K relevant document chunks (filtered by document_ids and owner_id)
  3. **Build context prompt**: format retrieved chunks into a system message
  4. **Call OpenAI** with context + user question
  5. **Return** response text + source citations
- **Configurable parameters** (in `app/config.py`):
  - `RAG_TOP_K: int = 5` — number of chunks to retrieve
  - `RAG_MAX_CONTEXT_TOKENS: int = 3000` — max tokens for context (leave room for response)
  - `RAG_RELEVANCE_THRESHOLD: float = 0.3` — minimum similarity score to include a chunk
- **Context window management**:
  - Count tokens in retrieved chunks (approximate: chars / 4)
  - Trim chunks to fit within `RAG_MAX_CONTEXT_TOKENS`
  - Include most relevant chunks first
- **System prompt template**:
  ```
  You are a helpful assistant for the Mnemos document management system.
  Answer the user's question based on the following document excerpts.
  If the excerpts don't contain relevant information, say so and answer from general knowledge.

  --- Document Excerpts ---
  [Source: {title}]
  {chunk_text}
  ---
  ```
- **Fallback**: if no relevant documents found (all below threshold), fall back to regular chat and note "No relevant documents found" in response

### 3. Conversation History (Stretch Goal)
- Store conversation messages in-memory or DB
- Include last N messages as context for follow-up questions
- This can be a separate issue if scope is too large

### 4. Updated Chat Route (`app/routes/ai.py`)
- Update `POST /api/v1/ai/chat` to use RAG when `use_rag=True`
- Return source citations in response
- **Backward compatible**: existing requests (without `use_rag` or `document_ids`) still work
- Existing `/api/v1/ai/test` endpoint unchanged

### 5. Streaming Responses (Stretch Goal)
- `POST /api/v1/ai/chat/stream` — SSE (Server-Sent Events) endpoint
  - Stream tokens as they arrive from OpenAI
  - Send sources as final SSE event
  - Improves perceived latency for long responses

### 6. Tests
- **RAG service tests** (mock embedding + vector search + OpenAI):
  - Question with relevant docs → response with sources
  - Question with no relevant docs → fallback to regular chat
  - Specific document scoping via `document_ids`
  - Context window management (chunks trimmed to fit)
  - Relevance threshold filtering
- **Route tests**:
  - RAG chat success → response with sources
  - `use_rag=False` → regular chat (no sources)
  - No OpenAI key → 503
  - Backward compatibility (old request format still works)

## Architecture Rules
- RAG service orchestrates embedding, vector, and OpenAI services
- Follow service layer rules — no direct HTTP concerns
- Backward compatibility is critical — don't break existing chat API
- Run `just harness` before committing

## Acceptance Criteria
- [ ] Chat answers questions using document context
- [ ] Source citations included in response (document title, relevant chunk, score)
- [ ] Can scope to specific documents via `document_ids`
- [ ] Relevance threshold filtering (don't include irrelevant chunks)
- [ ] Context window management (don't exceed token limits)
- [ ] Fallback to regular chat when no relevant docs found
- [ ] Backward compatible with existing chat requests
- [ ] Unit tests pass (~15+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #20 (Vector Embeddings) — needs embedding + Qdrant search
- Soft dependency on #21 (Search API) — can reuse search logic but not required
- Extends existing `app/routes/ai.py` and `app/models/ai.py`

## Effort Estimate
Large (~5–6 hours). Orchestration service, prompt engineering, context management.

## Parallel-Safe
Modifies existing files (`ai.py` models, routes). Best done after vector embeddings (#20) are merged.
```

---

### #23 — Authentication and authorization

```markdown
## Summary

Currently there is no authentication. All endpoints are open and there is no concept of a "current user." For a personal document management system, auth is needed to scope documents to users and protect the API.

## What to Build

### 1. Auth Strategy Decision
**Recommended: JWT-based authentication** (stateless, well-supported, standard for APIs).
- Access tokens: short-lived (30 minutes)
- Refresh tokens: long-lived (7 days), stored in DB for revocation
- For personal use, API key auth is simpler but JWT is more standard

### 2. User Model Extension
- Add `password_hash: str` column to the `User` ORM model
- Create Alembic migration to add the column
- Make `password_hash` nullable initially (existing users won't have passwords)

### 3. Auth Service (`app/services/auth_service.py`)
- `hash_password(password: str) -> str` — bcrypt hash
- `verify_password(password: str, hashed: str) -> bool` — bcrypt verify
- `create_access_token(user_id: UUID) -> str` — JWT with expiration
- `create_refresh_token(user_id: UUID) -> str` — longer-lived JWT
- `verify_token(token: str) -> TokenPayload` — decode and validate JWT, raise on invalid/expired
- **Password policy**: minimum 8 characters (configurable)

### 4. Auth Dependencies (`app/dependencies/auth.py`)
- `get_current_user(token: str = Depends(oauth2_scheme)) -> User`
  - Extract token from `Authorization: Bearer <token>` header
  - Verify token → get user_id → fetch user from DB
  - Raise 401 if invalid, expired, or user not found
- Can be used as `Depends(get_current_user)` in any protected route
- `get_optional_user()` — returns User | None (for endpoints that work with or without auth)

### 5. Auth Schemas (`app/models/auth.py`)
- `RegisterRequest` — email, display_name, password
- `LoginRequest` — email, password
- `TokenResponse` — access_token, refresh_token, token_type, expires_in
- `RefreshRequest` — refresh_token
- `TokenPayload` — user_id, exp, iat (internal, not API-facing)

### 6. Auth Routes (`app/routes/auth.py`)
- `POST /api/v1/auth/register` — create user + return tokens (201 Created)
- `POST /api/v1/auth/login` — email + password → tokens (200)
- `POST /api/v1/auth/refresh` — refresh_token → new access_token (200)
- `GET /api/v1/auth/me` — get current user profile (requires auth)
- Register router in `app/main.py`

### 7. Config Updates (`app/config.py`)
- `JWT_SECRET_KEY: str = "change-me-in-production"` — required for production
- `JWT_ALGORITHM: str = "HS256"`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30`
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7`
- `MIN_PASSWORD_LENGTH: int = 8`

### 8. Dependencies to Add (`pyproject.toml`)
- `pyjwt>=2.8.0` — JWT encoding/decoding (simpler than python-jose)
- `passlib[bcrypt]>=1.7.4` — password hashing
- `bcrypt>=4.0.0` — bcrypt backend

### 9. Route Protection Rollout
After auth is implemented, protect routes incrementally:
- **Phase 1 (this issue)**: Auth routes work, `get_current_user` dependency available
- **Phase 2 (separate issue)**: Add `Depends(get_current_user)` to document, tag, search routes
- **Always public**: health check endpoints, root endpoint
- Use `get_optional_user` for endpoints that benefit from auth but don't require it

### 10. Tests
- **Password tests**: hash + verify cycle, wrong password fails
- **Token tests**: create + verify cycle, expired token raises, invalid token raises
- **Auth dependency tests**: valid token → user, expired → 401, missing → 401, invalid → 401
- **Route tests**:
  - Register: success (201), duplicate email (409), weak password (422)
  - Login: success (200), wrong password (401), non-existent user (401)
  - Refresh: success, invalid refresh token (401)
  - Me: success with valid token, 401 without token

## Security Notes
- Never log passwords or tokens
- Use constant-time comparison for password verification (passlib handles this)
- JWT secret must be a strong random string in production
- Refresh tokens should be stored hashed in DB for revocation capability (stretch)
- Rate limit login attempts (stretch — separate issue)

## Architecture Rules
- Auth service is a new service — follows service layer rules
- Auth dependency lives in `app/dependencies/auth.py` (not middleware — it's per-route)
- Health check endpoints must remain public
- Run `just harness` before committing

## Acceptance Criteria
- [ ] User registration with email + password + display_name
- [ ] Login returns access_token and refresh_token
- [ ] Refresh endpoint issues new access_token
- [ ] `get_current_user` dependency available for route protection
- [ ] Token expiration works correctly
- [ ] Password hashing with bcrypt
- [ ] Health check endpoints remain public (no auth required)
- [ ] Unit tests pass (~25+ tests)
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #13 (User CRUD) — needs user service for user creation/lookup
- Requires Alembic migration to add `password_hash` to User model

## Effort Estimate
Large (~5–6 hours). Security-sensitive code, multiple services, token management.

## Parallel-Safe
Creates new files (`auth_service.py`, `auth.py` routes/models, `auth.py` dependencies). Shared edits: `config.py`, `main.py`, `pyproject.toml`, User ORM model + migration.
```

---

## New Issues to Create

### NEW: Frontend web application

```markdown
Title: Frontend web application (React + Vite)

## Summary

Mnemos has no frontend — only a FastAPI backend with OpenAPI docs. A modern web UI is essential for making this a usable document management system. This issue covers the initial frontend setup and core pages.

## What to Build

### 1. Project Setup (`frontend/`)
- **React 18+** with **TypeScript**
- **Vite** for fast dev/build
- **Tailwind CSS** for styling (utility-first, fast iteration)
- **React Router** for client-side routing
- **TanStack Query (React Query)** for server state management
- **Axios** or **fetch** wrapper for API calls

### 2. Core Layout
- Responsive sidebar navigation (collapsible on mobile)
- Top bar with search input and user menu
- Main content area with breadcrumbs
- Toast notifications for success/error feedback
- Dark mode support (Tailwind dark variant)

### 3. Pages

#### Dashboard (`/`)
- Document count, storage usage, recent uploads
- Quick upload dropzone
- Recent activity feed

#### Documents (`/documents`)
- Grid/list view toggle
- Sortable columns: title, date, size, type
- Tag filter sidebar
- Bulk actions: delete, tag, download
- Click to view document detail

#### Document Detail (`/documents/:id`)
- Document metadata (title, description, dates, tags)
- File preview (PDF viewer for PDFs, image viewer for images)
- Extracted text panel (collapsible)
- Tag management (add/remove tags inline)
- Download button
- Delete with confirmation

#### Upload (`/documents/upload` or modal)
- Drag-and-drop file upload zone
- Progress bar for upload
- Metadata form (title, description, tags)
- Multi-file upload support

#### Tags (`/tags`)
- Tag list with document counts
- Color-coded tag chips
- Create/edit/delete tags
- Click tag to see its documents

#### Search (`/search`)
- Full-text search with results
- Search type toggle (fulltext / semantic / hybrid)
- Filter panel (date range, tags, file type)
- Result cards with snippet highlights
- Click result to go to document

#### Chat (`/chat`)
- Chat interface with message bubbles
- Source citations with links to documents
- Document scope selector (chat about specific docs)
- Conversation history (session-based)

#### Settings / Profile (`/settings`)
- User profile display
- Password change (when auth is implemented)
- API key display (if applicable)

### 4. Docker Integration
- Add frontend service to `docker-compose.yml` (Vite dev server in development)
- Production build served by nginx or similar
- Proxy API requests to backend (`/api/v1/*` → `http://backend:8000`)

### 5. API Client
- Auto-generate TypeScript types from OpenAPI schema (`openapi-typescript`)
- Type-safe API client layer
- Error handling with user-friendly messages
- Auth token management (when auth is implemented)

## Design Principles
- **Clean and minimal**: no visual clutter, focus on content
- **Responsive**: works on desktop, tablet, and mobile
- **Fast**: optimistic updates, prefetching, lazy loading
- **Accessible**: proper ARIA labels, keyboard navigation, focus management

## Acceptance Criteria
- [ ] Project setup with Vite + React + TypeScript + Tailwind
- [ ] Sidebar navigation with responsive layout
- [ ] Document list page with grid/list views
- [ ] Document upload with drag-and-drop
- [ ] Tag management page
- [ ] Search page with filters
- [ ] Chat interface
- [ ] Docker integration (dev + production)
- [ ] API client with TypeScript types

## Dependencies
- Best started after core API routes are merged (#12, #13, #14)
- Can be developed in parallel using OpenAPI docs for mock data
- Auth integration (#23) can be added incrementally

## Effort Estimate
Extra-large (~15–20 hours). Full frontend application with multiple pages.

## Parallel-Safe
Yes — entirely new `frontend/` directory. Only shared edit: `docker-compose.yml`.
```

---

### NEW: Background job processing (extraction + embedding pipeline)

```markdown
Title: Background job processing for extraction and embedding pipeline

## Summary

PDF text extraction (#18) and vector embedding (#20) are CPU-intensive and can take seconds to minutes for large files. Running them synchronously during file upload creates poor UX (long upload times, timeouts). This issue adds background job processing so uploads return instantly and processing happens asynchronously.

## What to Build

### 1. Job Queue Infrastructure
- **Option A (Recommended for v1)**: In-process background tasks using FastAPI `BackgroundTasks`
  - Simple, no extra infrastructure
  - Sufficient for personal use (low concurrency)
  - Jobs lost on server restart (acceptable for v1)
- **Option B (Production-ready)**: Celery + Redis or ARQ (async Redis queue)
  - Persistent job queue
  - Retries, monitoring, concurrency control
  - Add Redis to `docker-compose.yml`
  - Implement as v2 upgrade

### 2. Document Processing Pipeline
When a document is uploaded:
1. **Upload** → save file, create Document record with `status="uploaded"` → return 201 immediately
2. **Background**: Extract text → update `extracted_text` + `status="extracted"`
3. **Background**: Generate embeddings → store in Qdrant + `status="embedded"`
4. **On failure**: set `status="error"`, log details, allow manual retry

### 3. Document Status Tracking
- Add `processing_status` field to Document model (Alembic migration):
  - `uploaded` — file saved, no processing yet
  - `extracting` — text extraction in progress
  - `extracted` — text extraction complete
  - `embedding` — vector embedding in progress
  - `ready` — fully processed (text + vectors)
  - `error` — processing failed
- Add `processing_error` field: `str | None` — error message if failed

### 4. Status API
- `GET /api/v1/documents/{id}/status` — return processing status
- Include `processing_status` in DocumentResponse

### 5. Manual Retry
- `POST /api/v1/documents/{id}/reprocess` — restart the extraction + embedding pipeline
- Only allowed when `status` is `error` or `ready` (re-process)

### 6. Tests
- Pipeline orchestration tests (mock extraction + embedding services)
- Status transitions (uploaded → extracting → extracted → embedding → ready)
- Error handling (extraction fails → status = error)
- Retry logic

## Acceptance Criteria
- [ ] File upload returns immediately (no blocking on extraction/embedding)
- [ ] Document processing_status tracks progress
- [ ] Status endpoint shows current processing state
- [ ] Error state with retry capability
- [ ] Extraction and embedding run in background
- [ ] Unit tests pass
- [ ] `just harness` passes cleanly

## Dependencies
- **Hard dependency** on #17 (File Upload) — pipeline starts after upload
- **Hard dependency** on #18 (PDF Extraction) — pipeline step 1
- **Hard dependency** on #20 (Vector Embeddings) — pipeline step 2

## Effort Estimate
Medium (~4 hours for v1 with BackgroundTasks). Large (~8 hours for v2 with Celery/ARQ).

## Parallel-Safe
Modifies Document model (migration) and upload route. Best started after #17, #18, #20 are merged.
```

---

## Execution Roadmap

### NEW: Master execution roadmap (tracking issue)

```markdown
Title: Execution Roadmap: Mnemos MVP

## Vision

Mnemos is a personal RAG system for managing documents with intelligent search and chat. The MVP delivers: upload documents, extract text, search (full-text + semantic), and chat with your documents.

## Current State

- [x] Project scaffolding (FastAPI, PostgreSQL, Docker Compose, CI)
- [x] Database ORM models + migrations (User, Document, Tag, DocumentTag)
- [x] Health check endpoints
- [x] OpenAI chat proxy (basic, no RAG)
- [x] Code quality tooling (Ruff, Pyright, structural linter, `just harness`)

## Phase 1: Foundation CRUDs (No Dependencies)
> **Goal**: All three entity CRUD APIs working with full test coverage.
> **Estimated effort**: ~6 hours total | **Parallelism**: All three can run simultaneously

| Issue | Title | Status | PR |
|---|---|---|---|
| #14 | Tag CRUD | **Done** | PR #30 |
| #12 | Document CRUD | **PR Open** | PR #29 — review & merge |
| #13 | User CRUD | **Ready** | Not started |

**Merge order**: Any order (no dependencies between them).

## Phase 2: Relationships & File Handling
> **Goal**: Documents can be uploaded, downloaded, and tagged.
> **Estimated effort**: ~8 hours total | **Parallelism**: #15 after #12+#14; #17 after #12

| Issue | Title | Depends On | Status |
|---|---|---|---|
| #15 | Document-Tag association | #12, #14 | Ready after Phase 1 |
| #17 | File upload & storage | #12 | Ready after #12 merged |

**Merge order**: #15 and #17 can run in parallel once their deps are met.

## Phase 3: Intelligence Pipeline
> **Goal**: Uploaded documents are automatically processed — text extracted, embeddings stored.
> **Estimated effort**: ~12 hours total | **Parallelism**: #18 first, then #20, then background jobs

| Issue | Title | Depends On | Status |
|---|---|---|---|
| #18 | PDF text extraction | #12, #17 | Ready after Phase 2 |
| #20 | Vector embeddings + Qdrant | #18 | Ready after #18 |
| NEW | Background job processing | #17, #18, #20 | Ready after all three |

**Merge order**: Sequential — #18 → #20 → background jobs.

## Phase 4: Search & Chat
> **Goal**: Users can search documents and chat with their document knowledge base.
> **Estimated effort**: ~12 hours total | **Parallelism**: #21 and #22 after #20

| Issue | Title | Depends On | Status |
|---|---|---|---|
| #21 | Search API (full-text + semantic) | #12, #20 | Ready after Phase 3 |
| #22 | RAG-powered document chat | #20 | Ready after Phase 3 |

**Merge order**: #21 and #22 can run in parallel.

## Phase 5: Security & Frontend
> **Goal**: Auth-protected API with a beautiful web interface.
> **Estimated effort**: ~20+ hours total | **Parallelism**: #23 after #13; Frontend independent

| Issue | Title | Depends On | Status |
|---|---|---|---|
| #23 | Authentication & authorization | #13 | Ready after #13 |
| NEW | Frontend web application | Phase 1–4 APIs | Can start during Phase 2 |

**Merge order**: Auth first (other routes will need protection), then frontend.

## Dependency Graph

```
Phase 1 (Foundation)           Phase 2 (Files & Tags)     Phase 3 (Intelligence)       Phase 4 (Search & Chat)    Phase 5 (Security & UI)
─────────────────────          ──────────────────────      ─────────────────────────     ──────────────────────     ──────────────────────
#14 Tag CRUD ─────────────┐
                           ├──► #15 Doc-Tag Association
#12 Document CRUD ────────┤
                           └──► #17 File Upload ──────► #18 PDF Extraction ──────► #20 Embeddings ──┬──► #21 Search API
                                                                                                     ├──► #22 RAG Chat
                                                                                                     └──► BG Jobs

#13 User CRUD ──────────────────────────────────────────────────────────────────────────────────────► #23 Auth

                                Frontend (can start here, grows with each phase) ────────────────────────────────────►
```

## Issue Checklist

- [ ] #14 Tag CRUD — **DONE** (merge PR)
- [ ] #12 Document CRUD — **PR OPEN** (review & merge)
- [ ] #13 User CRUD — ready to implement
- [ ] #15 Document-Tag association — after #12 + #14
- [ ] #17 File upload & storage — after #12
- [ ] #18 PDF text extraction — after #17
- [ ] #20 Vector embeddings & Qdrant — after #18
- [ ] #21 Document search API — after #20
- [ ] #22 RAG-powered document chat — after #20
- [ ] #23 Authentication — after #13
- [ ] Background job processing (NEW) — after #17, #18, #20
- [ ] Frontend web application (NEW) — can start during Phase 2
- [ ] #19 test — **CLOSE** (empty junk issue)

## Definition of Done (MVP)
- All CRUD APIs working with tests
- File upload with automatic text extraction and embedding
- Full-text + semantic search
- RAG chat with document citations
- JWT authentication
- Frontend with document management, search, and chat
- `just harness` passes on every merge
```
