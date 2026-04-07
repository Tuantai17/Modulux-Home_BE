from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    site_settings,
    banners,
    core_features,
    projects,
    project_images,
    categories,
    posts,
    pages,
    faqs,
    videos,
    partners,
    contacts,
    subscribers,
    menus,
    search,
    blogs,
    blog_admin,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(site_settings.router)
api_router.include_router(banners.router)
api_router.include_router(core_features.router)
api_router.include_router(projects.router)
api_router.include_router(project_images.router)
api_router.include_router(categories.router)
api_router.include_router(posts.router)
api_router.include_router(pages.router)
api_router.include_router(faqs.router)
api_router.include_router(videos.router)
api_router.include_router(partners.router)
api_router.include_router(contacts.router)
api_router.include_router(subscribers.router)
api_router.include_router(menus.router)
api_router.include_router(search.router)
api_router.include_router(blogs.router)
api_router.include_router(blog_admin.router)
