# Readloom Enhancement Tickets

This document breaks down the hybrid UI implementation plan into discrete enhancement tickets that can be tracked separately.

## Backend Enhancements

### Ticket B1: Content Type System and Service Factory

**Description:**
Implement a content type system and service factory to route requests to the appropriate service based on content type.

**Tasks:**
1. Create ContentType enum
2. Implement content service factory
3. Create base service interface
4. Add unit tests for the factory

**Files to modify:**
- Create `backend/features/content_service_factory.py`
- Create `backend/features/content_service_base.py`

**Dependencies:**
- None

---

### Ticket B2: Book-Specific Service Implementation

**Description:**
Implement a book-specific service that handles books differently from manga, focusing on author-based organization.

**Tasks:**
1. Create BookService class implementing ContentServiceBase
2. Implement book-specific search
3. Implement book-specific details retrieval
4. Implement book-specific import logic
5. Implement author-based folder structure creation

**Files to modify:**
- Create `backend/features/book_service.py`

**Dependencies:**
- B1: Content Type System and Service Factory

---

### Ticket B3: Manga-Specific Service Implementation

**Description:**
Adapt existing manga handling into a manga-specific service that implements the common interface.

**Tasks:**
1. Create MangaService class implementing ContentServiceBase
2. Adapt existing manga search logic
3. Adapt existing manga details retrieval
4. Adapt existing manga import logic
5. Adapt existing series-based folder structure creation

**Files to modify:**
- Create `backend/features/manga_service.py`

**Dependencies:**
- B1: Content Type System and Service Factory

---

### Ticket B4: Folder Structure Helper Updates

**Description:**
Update folder creation helpers to use the appropriate service based on content type.

**Tasks:**
1. Update folder creation helper to use content service factory
2. Ensure backward compatibility with existing code
3. Add unit tests for folder creation

**Files to modify:**
- Update `backend/base/helpers.py`

**Dependencies:**
- B1: Content Type System and Service Factory
- B2: Book-Specific Service Implementation
- B3: Manga-Specific Service Implementation

---

## Database Enhancements

### Ticket D1: Author Database Schema

**Description:**
Create database schema for authors and book-author relationships.

**Tasks:**
1. Create authors table
2. Create book_authors relationship table
3. Add is_book column to series table
4. Write migration script

**Files to modify:**
- Create `backend/migrations/0007_add_authors_table.py`

**Dependencies:**
- None

---

### Ticket D2: Data Migration for Existing Books

**Description:**
Migrate existing book data to use the new author-based schema.

**Tasks:**
1. Extract author information from existing books
2. Populate the authors table
3. Create book-author relationships
4. Mark existing books with is_book flag

**Files to modify:**
- Update `backend/migrations/0007_add_authors_table.py` or create a new migration

**Dependencies:**
- D1: Author Database Schema

---

### Ticket D3: Folder Structure Migration

**Description:**
Create a script to reorganize the folder structure for books to be author-based.

**Tasks:**
1. Create script to identify book folders
2. Create author folders
3. Move book folders into appropriate author folders
4. Handle edge cases and errors

**Files to modify:**
- Create `scripts/migrate_book_folders.py`

**Dependencies:**
- D1: Author Database Schema
- D2: Data Migration for Existing Books
- B4: Folder Structure Helper Updates

---

## API Enhancements

### Ticket A1: Content-Type Aware API Endpoints

**Description:**
Update API endpoints to handle content type and route to appropriate services.

**Tasks:**
1. Update metadata API endpoints to use content service factory
2. Add content_type parameter to relevant endpoints
3. Ensure backward compatibility

**Files to modify:**
- Update `frontend/api_metadata_fixed.py`
- Update `frontend/api_ebooks.py`

**Dependencies:**
- B1: Content Type System and Service Factory
- B2: Book-Specific Service Implementation
- B3: Manga-Specific Service Implementation

---

### Ticket A2: Author API Endpoints

**Description:**
Create new API endpoints for author-related operations.

**Tasks:**
1. Create endpoint to get all authors
2. Create endpoint to get books by author
3. Create endpoint to get author details
4. Create endpoint to search authors

**Files to modify:**
- Create `frontend/api_authors.py`

**Dependencies:**
- D1: Author Database Schema
- D2: Data Migration for Existing Books

---

## Frontend Enhancements

### Ticket F1: Base Template with Content Type Selector

**Description:**
Update the base template to include a content type selector.

**Tasks:**
1. Add content type selector to navigation
2. Add JavaScript to handle content type switching
3. Update CSS for content type selector
4. Add content type to template context

**Files to modify:**
- Update `frontend/templates/base.html`
- Update `frontend/static/css/style.css`
- Update `frontend/static/js/main.js` (if exists)

**Dependencies:**
- None

---

### Ticket F2: Content-Specific Layouts

**Description:**
Create content-specific layout templates for books and manga.

**Tasks:**
1. Create books layout template
2. Create manga layout template
3. Ensure proper inheritance from base template
4. Add content-specific sidebar components

**Files to modify:**
- Create `frontend/templates/books_layout.html`
- Create `frontend/templates/manga_layout.html`

**Dependencies:**
- F1: Base Template with Content Type Selector

---

### Ticket F3: Book-Specific Views

**Description:**
Create book-specific view templates focusing on author-based organization.

**Tasks:**
1. Create book search template
2. Create author view template
3. Create book detail template
4. Update JavaScript for book-specific interactions

**Files to modify:**
- Create `frontend/templates/books/search.html`
- Create `frontend/templates/books/author.html`
- Create `frontend/templates/books/book.html`
- Create `frontend/static/js/books.js`

**Dependencies:**
- F2: Content-Specific Layouts

---

### Ticket F4: Manga-Specific Views

**Description:**
Adapt existing templates to manga-specific view templates focusing on series-based organization.

**Tasks:**
1. Create manga search template
2. Create series view template
3. Create chapter view template
4. Update JavaScript for manga-specific interactions

**Files to modify:**
- Create `frontend/templates/manga/search.html`
- Create `frontend/templates/manga/series.html`
- Create `frontend/templates/manga/chapter.html`
- Create `frontend/static/js/manga.js`

**Dependencies:**
- F2: Content-Specific Layouts

---

### Ticket F5: Route Updates

**Description:**
Update UI routes to handle content type-specific views.

**Tasks:**
1. Add content type to route context
2. Create book-specific routes
3. Create manga-specific routes
4. Add home route with content type detection

**Files to modify:**
- Update `frontend/ui.py`

**Dependencies:**
- F3: Book-Specific Views
- F4: Manga-Specific Views

---

## Testing and Refinement

### Ticket T1: Unit and Integration Tests

**Description:**
Create comprehensive tests for the new content type system.

**Tasks:**
1. Write unit tests for content service factory
2. Write unit tests for book and manga services
3. Write integration tests for API endpoints
4. Write tests for database migrations

**Files to modify:**
- Create test files in appropriate directories

**Dependencies:**
- All backend and database tickets

---

### Ticket T2: UI Testing and Refinement

**Description:**
Test and refine the UI for both content types.

**Tasks:**
1. Test content type switching
2. Test book search and browsing
3. Test manga search and browsing
4. Refine UI based on testing feedback

**Files to modify:**
- Various frontend files as needed

**Dependencies:**
- All frontend tickets

---

## Deployment and Documentation

### Ticket P1: User Documentation

**Description:**
Create user documentation for the new content type system.

**Tasks:**
1. Document how to use the content type selector
2. Document book vs. manga organization differences
3. Document migration process for existing users
4. Update screenshots and examples

**Files to modify:**
- Update existing documentation
- Create new documentation as needed

**Dependencies:**
- All implementation tickets

---

### Ticket P2: Deployment Plan

**Description:**
Create a deployment plan for rolling out the changes.

**Tasks:**
1. Define deployment steps
2. Create rollback plan
3. Define monitoring metrics
4. Schedule deployment windows

**Files to modify:**
- Create deployment documentation

**Dependencies:**
- All implementation tickets

---

## Implementation Order

For the most efficient implementation, follow this order with the recommended branches:

1. **Backend Foundation** (`feature/content-type-system` branch)
   - B1: Content Type System and Service Factory
   - D1: Author Database Schema

2. **Core Services**
   - **Book Service** (`feature/book-service` branch)
     - B2: Book-Specific Service Implementation
     - D2: Data Migration for Existing Books
     - A2: Author API Endpoints
   - **Manga Service** (`feature/manga-service` branch)
     - B3: Manga-Specific Service Implementation
     - A1: Content-Type Aware API Endpoints
   - **Folder Structure** (`feature/folder-structure` branch)
     - B4: Folder Structure Helper Updates
     - D3: Folder Structure Migration

3. **Frontend Implementation**
   - **UI Foundation** (`feature/frontend-base` branch)
     - F1: Base Template with Content Type Selector
     - F2: Content-Specific Layouts
     - F5: Route Updates
   - **Content Views** (`feature/content-views` branch)
     - F3: Book-Specific Views
     - F4: Manga-Specific Views

4. **Testing and Finalization** (can be implemented across all branches)
   - T1: Unit and Integration Tests
   - T2: UI Testing and Refinement
   - P1: User Documentation
   - P2: Deployment Plan

### Branch Merge Order

1. `feature/content-type-system` → Hybrid-UI-Split
2. `feature/book-service` → Hybrid-UI-Split
3. `feature/manga-service` → Hybrid-UI-Split
4. `feature/folder-structure` → Hybrid-UI-Split
5. `feature/frontend-base` → Hybrid-UI-Split
6. `feature/content-views` → Hybrid-UI-Split
