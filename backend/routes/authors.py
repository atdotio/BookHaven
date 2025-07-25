from flask import Blueprint, jsonify
from models.epub_metadata import EpubMetadata
from functions.db import get_session
from functions.roles import login_required

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/api/authors', methods=['GET'])
@login_required
def get_authors():
    """
    Returns a list of distinct authors sorted alphabetically.
    """
    session = get_session()
    total_books = session.query(EpubMetadata.id).count()
    if total_books == 0:
        return jsonify({
            "authors": [],
            "total_authors": 0
        })
    authors_query = session.query(EpubMetadata.authors).all()
    authors = set()
    for entry in authors_query:
        if entry.authors:
            authors.update([author.strip() for author in entry.authors.split(",")])
    sorted_authors = sorted(authors)
    return jsonify({
        "authors": sorted_authors,
        "total_authors": len(sorted_authors)
    })

@authors_bp.route('/api/authors/<string:author_name>', methods=['GET'])
@login_required
def get_author_books(author_name):
    """
    Returns all books by a specific author.
    """
    session = get_session()
    normalized_author_name = author_name.replace('-', ' ').lower()
    author_query = session.query(EpubMetadata).filter(
        EpubMetadata.authors.ilike(f"%{normalized_author_name}%")
    ).all()
    if not author_query:
        return jsonify({"error": f"No books found for author: {author_name}"}), 404
    books = [{
        "id": book.id,
        "title": book.title,
        "authors": book.authors.split(", "),
        "series": book.series,
        "seriesindex": book.seriesindex,
        "coverUrl": f"/api/covers/{book.identifier}",
        "relative_path": book.relative_path,
        "identifier": book.identifier,
    } for book in author_query]
    return jsonify({
        "author": author_name,
        "books": books,
        "total_books": len(books)
    }), 200