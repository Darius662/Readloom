# Author Collection Management

This document describes the author collection management feature in Readloom, which allows you to organize your books by author with a consistent folder structure.

## Overview

The author collection management feature allows you to:

1. Add authors to your collections with a proper folder structure
2. Create author folders with subfolders for their notable works
3. Generate README.md files with author information
4. Add more books to existing author folders
5. Maintain a consistent folder organization for authors and their books

## Folder Structure

When you add an author to your collection, Readloom creates the following folder structure:

```
Root Folder/
└── Author Name/
    ├── README.md (contains author information)
    ├── Notable Work 1/
    ├── Notable Work 2/
    └── ...
```

When you add a book to your collection, Readloom creates a folder for the book inside the author's folder:

```
Root Folder/
└── Author Name/
    ├── README.md
    ├── Book Title 1/
    ├── Book Title 2/
    └── ...
```

## Adding Authors to Collections

To add an author to your collection:

1. Search for the author using the search bar
2. Click on the author card to view the author details
3. Click the "Add Author to Collection" button
4. Select a collection and root folder (if applicable)
5. Click "Add to Collection"

Readloom will create a folder for the author in the selected root folder, along with subfolders for their notable works. It will also generate a README.md file with the author's information, including:

- Name
- Birth/death dates
- Biography
- Notable works
- Subjects/genres
- Links to external resources

## Adding Books to Existing Authors

If an author is already in your collection, you can still add more books by that author:

1. Search for a book by the author
2. Click on the book card to view the book details
3. Click the "Add to Collection" button
4. Select a collection and root folder (if applicable)
5. Click "Add to Collection"

Readloom will add the book to the existing author's folder, creating a new subfolder for the book.

If you try to add an author who is already in your collection, Readloom will show a message indicating that the author already exists and provide a button to search for books by that author.

## Author Database

Readloom stores author information in the following database tables:

- `authors`: Stores basic author information (name, provider, provider_id, etc.)
- `collection_authors`: Links authors to collections
- `author_books`: Links authors to books

This allows Readloom to maintain relationships between authors, books, and collections, ensuring a consistent folder structure.

## API Endpoints

The following API endpoints are used for author collection management:

- `/api/metadata/author/import/<provider>/<author_id>`: Import an author to the collection
- `/api/metadata/enhanced_import/<provider>/<book_id>`: Import a book to the collection with author folder structure

These endpoints handle the creation of folders, subfolders, and README.md files, as well as the database operations required to maintain the relationships between authors, books, and collections.

## Benefits

The author collection management feature provides several benefits:

1. **Organized Library**: Books are organized by author, making it easy to find all books by a particular author
2. **Consistent Structure**: All authors and books follow the same folder structure
3. **Rich Metadata**: README.md files provide detailed information about authors
4. **Flexible Organization**: You can add more books to existing authors at any time
5. **Efficient Workflow**: The UI guides you through the process of adding authors and books
