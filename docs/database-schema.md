# Database Schema Documentation

## Overview

The Mnemos database uses PostgreSQL with SQLAlchemy ORM and Alembic migrations. The schema consists of four main tables: `users`, `documents`, `tags`, and a many-to-many association table `document_tags`.

## Database Connection

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy (async)
- **Connection**: asyncpg driver
- **Migrations**: Alembic

## Tables

### users

Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEXED | User email address |
| display_name | VARCHAR(255) | NOT NULL | User display name |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Relationships:**
- One-to-many with `documents` (owner)

### documents

Stores uploaded documents (PDFs, receipts, manuals, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique document identifier |
| title | VARCHAR(500) | NOT NULL | Document title |
| description | TEXT | NULL | Optional document description |
| filename | VARCHAR(500) | NOT NULL | Original filename |
| file_path | VARCHAR(1000) | NOT NULL | Storage path |
| file_size_bytes | INTEGER | NOT NULL | File size in bytes |
| mime_type | VARCHAR(100) | NOT NULL, DEFAULT 'application/pdf' | MIME type |
| extracted_text | TEXT | NULL | Extracted text content |
| owner_id | UUID | NOT NULL, INDEXED, FOREIGN KEY | Reference to users(id) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Upload timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Last update timestamp |

**Relationships:**
- Many-to-one with `users` (owner)
- Many-to-many with `tags` (via `document_tags`)

**Foreign Keys:**
- `owner_id` → `users(id)` ON DELETE CASCADE

### tags

Stores tags for categorizing documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique tag identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE, INDEXED | Tag name |
| color | VARCHAR(7) | NULL | Optional hex color code |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT now() | Tag creation timestamp |

**Relationships:**
- Many-to-many with `documents` (via `document_tags`)

### document_tags

Association table for many-to-many relationship between documents and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | UUID | PRIMARY KEY (composite), FOREIGN KEY | Reference to documents(id) |
| tag_id | UUID | PRIMARY KEY (composite), FOREIGN KEY | Reference to tags(id) |

**Foreign Keys:**
- `document_id` → `documents(id)` ON DELETE CASCADE
- `tag_id` → `tags(id)` ON DELETE CASCADE

## Database Schema Proof

Below is the actual database schema output from PostgreSQL:

### List of Tables

```
              List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | document_tags   | table | postgres
 public | documents       | table | postgres
 public | tags            | table | postgres
 public | users           | table | postgres
(5 rows)
```

### Users Table Structure

```
                                                      Table "public.users"
    Column    |           Type           | Collation | Nullable | Default | Storage  | Compression | Stats target | Description 
--------------+--------------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 id           | uuid                     |           | not null |         | plain    |             |              | 
 email        | character varying(255)   |           | not null |         | extended |             |              | 
 display_name | character varying(255)   |           | not null |         | extended |             |              | 
 created_at   | timestamp with time zone |           | not null | now()   | plain    |             |              | 
 updated_at   | timestamp with time zone |           | not null | now()   | plain    |             |              | 
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "ix_users_email" UNIQUE, btree (email)
Referenced by:
    TABLE "documents" CONSTRAINT "documents_owner_id_fkey" FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
```

### Documents Table Structure

```
                                                                    Table "public.documents"
     Column      |           Type           | Collation | Nullable |               Default                | Storage  | Compression | Stats target | Description 
-----------------+--------------------------+-----------+----------+--------------------------------------+----------+-------------+--------------+-------------
 id              | uuid                     |           | not null |                                      | plain    |             |              | 
 title           | character varying(500)   |           | not null |                                      | extended |             |              | 
 description     | text                     |           |          |                                      | extended |             |              | 
 filename        | character varying(500)   |           | not null |                                      | extended |             |              | 
 file_path       | character varying(1000)  |           | not null |                                      | extended |             |              | 
 file_size_bytes | integer                  |           | not null |                                      | plain    |             |              | 
 mime_type       | character varying(100)   |           | not null | 'application/pdf'::character varying | extended |             |              | 
 extracted_text  | text                     |           |          |                                      | extended |             |              | 
 owner_id        | uuid                     |           | not null |                                      | plain    |             |              | 
 created_at      | timestamp with time zone |           | not null | now()                                | plain    |             |              | 
 updated_at      | timestamp with time zone |           | not null | now()                                | plain    |             |              | 
Indexes:
    "documents_pkey" PRIMARY KEY, btree (id)
    "ix_documents_owner_id" btree (owner_id)
Foreign-key constraints:
    "documents_owner_id_fkey" FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
Referenced by:
    TABLE "document_tags" CONSTRAINT "document_tags_document_id_fkey" FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
```

### Tags Table Structure

```
                                                     Table "public.tags"
   Column   |           Type           | Collation | Nullable | Default | Storage  | Compression | Stats target | Description 
------------+--------------------------+-----------+----------+---------+----------+-------------+--------------+-------------
 id         | uuid                     |           | not null |         | plain    |             |              | 
 name       | character varying(100)   |           | not null |         | extended |             |              | 
 color      | character varying(7)     |           |          |         | extended |             |              | 
 created_at | timestamp with time zone |           | not null | now()   | plain    |             |              | 
Indexes:
    "tags_pkey" PRIMARY KEY, btree (id)
    "ix_tags_name" UNIQUE, btree (name)
Referenced by:
    TABLE "document_tags" CONSTRAINT "document_tags_tag_id_fkey" FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
```

### Document_Tags Table Structure

```
                                       Table "public.document_tags"
   Column    | Type | Collation | Nullable | Default | Storage | Compression | Stats target | Description 
-------------+------+-----------+----------+---------+---------+-------------+--------------+-------------
 document_id | uuid |           | not null |         | plain   |             |              | 
 tag_id      | uuid |           | not null |         | plain   |             |              | 
Indexes:
    "document_tags_pkey" PRIMARY KEY, btree (document_id, tag_id)
Foreign-key constraints:
    "document_tags_document_id_fkey" FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    "document_tags_tag_id_fkey" FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
```

## Migrations

The initial migration (revision `6694aaa8eac8`) creates all four tables with proper indexes and foreign key constraints.

To run migrations:

```bash
cd backend
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/mnemos" uv run alembic upgrade head
```

## Indexes

- `users.email` - B-tree index for fast email lookups (unique constraint)
- `tags.name` - B-tree index for fast tag name lookups (unique constraint)
- `documents.owner_id` - B-tree index for fast user document queries
- `document_tags` - Composite primary key provides efficient many-to-many lookups

## Cascade Deletions

All foreign key relationships use `ON DELETE CASCADE`:
- Deleting a user deletes all their documents
- Deleting a document removes all its tag associations
- Deleting a tag removes all its document associations
