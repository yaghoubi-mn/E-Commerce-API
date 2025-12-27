from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path


router = DefaultRouter()
router.register(r"categories", views.CategoryViews, basename="categories")
router.register(r"products", views.ProductViews, basename="products")
router.register(r"carts", views.CartViews, basename="carts")
router.register(r'discounts', views.DiscountViewSet, basename='discounts')

urlpatterns = [
    path("carts/me/", views.GetCartView.as_view(), name="carts-me"),
    path("carts/me/items/", views.UserCart.as_view(), name="carts-me-items"),
    path(
        "carts/me/items/<int:item_id>/",
        views.UserCart.as_view(),
        name="carts-me-items-delete",
    ),

    # GET LIST and POST CREATE for comments
    path('products/<int:product_id>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='product-comments-list'),

    # PUT and DELETE for comments
    path('comments/<int:comment_id>/', views.CommentViewSet.as_view({
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),

    # upvote and downvote for comments
    path('comments/<int:comment_id>/upvote/', views.CommentViewSet.as_view({'post': 'upvote'}), name='comment-upvote'),
    path('comments/<int:comment_id>/downvote/', views.CommentViewSet.as_view({'post': 'downvote'}), name='comment-downvote'),

] + router.urls
