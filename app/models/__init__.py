# Import all models so SQLAlchemy can discover them
from app.models.user import User  # noqa: F401
from app.models.site import SiteSetting, Banner, CoreFeature, Video, Partner  # noqa: F401
from app.models.project import Project, ProjectImage  # noqa: F401
from app.models.blog import Category, Post  # noqa: F401
from app.models.blog_sync import Blog, SyncLog  # noqa: F401
from app.models.page import Page, Faq  # noqa: F401
from app.models.contact import Contact, Subscriber  # noqa: F401
