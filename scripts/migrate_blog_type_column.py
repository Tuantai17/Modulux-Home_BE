from app.services.blog_sync_service import ensure_blog_sync_schema


def main() -> None:
    ensure_blog_sync_schema()
    print("Blog type column is ready.")


if __name__ == "__main__":
    main()
