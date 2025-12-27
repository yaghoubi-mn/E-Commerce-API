from django.db import transaction
from django.db.models import F
from rest_framework import permissions
from rest_framework.decorators import action
from products.serializers import CategorySerializer, CommentReadSerializer, CommentWriteSerializer, DiscountSerializer, ProductSerializer, CartSerializer
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from products.models import Category, Comment, CommentVote, Discount, Product, Cart
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from products.permission import IsAdminOrReadOnly, IsAdminUser, IsOwnerOrReadOnly
import json


class CategoryViews(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Category.objects.all()

class ProductViews(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Product.objects.all()


class CartViews(viewsets.ModelViewSet):

    serializer_class = CartSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]
    queryset = Cart.objects.all()


class GetCartView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, format="json"):
        cart, _ = Cart.objects.get_or_create(
            user_id=self.request.user,
            defaults={"expires_at": datetime.now() + timedelta(days=7)},
        )

        return Response(CartSerializer(cart).data)


class UserCart(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_cart(self):
        cart = Cart.objects.get(user_id=self.request.user)

        return cart

    def post(self, request, format="json"):
        cart = self.get_cart()
        cartItems = cart.items
        items = request.data

        if not isinstance(items, list):
            return Response({"detail": "Invalid item format"}, status=400)

        for item in items:
            if not isinstance(item, dict):
                return Response({"detail": "Invalid item format"}, status=400)
            product = get_object_or_404(Product, pk=item.get("product_id"))
            cartItems.append(item)
        cart.items = json.dumps(cartItems)
        cart.save()

        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id=None):
        cart = self.get_cart()

        before = len(cart.items)

        cart.items = [i for i in cart.items if str(i.get("product_id")) != str(item_id)]
        after = len(cart.items)

        if before == after:
            return Response({"detail": "Item not found."}, status=404)

        cart.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_204_NO_CONTENT)



class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_url_kwarg = 'comment_id'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentWriteSerializer
        return CommentReadSerializer

    def get_queryset(self):
        """
        Dynamic queryset based on the action.
        """
        # 1. For Detail actions (PUT, DELETE), we look up by comment ID globally.
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return Comment.objects.all()

        # 2. For List action (GET), we must filter by the Product ID in the URL.
        product_id = self.kwargs.get('product_id')
        return Comment.objects.filter(product_id=product_id, is_approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Handle POST /products/{id}/comments
        """
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        
        # TODO: verify
        # is_verified_purchase = check_verified(self.request.user, product)
        
        serializer.save(
            user=self.request.user,
            product=product,
            is_verified_purchase=False,
            is_approved=False
        )

    def perform_update(self, serializer):
        """
        Handle PUT /comments/{id}
        """
        # Reset approval if content changes
        serializer.save(is_approved=False)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upvote(self, request, comment_id=None):
        return self._perform_vote(request.user, comment_id, is_helpful=True)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def downvote(self, request, comment_id=None):
        return self._perform_vote(request.user, comment_id, is_helpful=False)

    def _perform_vote(self, user, comment_id, is_helpful):
        """
        Internal logic to handle voting.
        Handles: New votes, Switching votes (Up -> Down), and Toggling off (Up -> No vote).
        """
        comment = get_object_or_404(Comment, pk=comment_id)

        with transaction.atomic():

            vote_query = CommentVote.objects.filter(user=user, comment=comment)
            
            if vote_query.exists():
                vote = vote_query.first()
                
                if vote.is_helpful == is_helpful:
                    # User is voting the SAME thing again: Undo the vote (Toggle off)
                    vote.delete()
                    if is_helpful:
                        comment.helpful_count = F('helpful_count') - 1
                    else:
                        comment.unhelpful_count = F('unhelpful_count') - 1
                    message = "Vote removed"
                
                else:
                    # User is SWITCHING vote (e.g., Up -> Down)
                    vote.is_helpful = is_helpful
                    vote.save()
                    
                    if is_helpful:
                        # Was unhelpful, now helpful
                        comment.unhelpful_count = F('unhelpful_count') - 1
                        comment.helpful_count = F('helpful_count') + 1
                    else:
                        # Was helpful, now unhelpful
                        comment.helpful_count = F('helpful_count') - 1
                        comment.unhelpful_count = F('unhelpful_count') + 1
                    message = "Vote changed"
            
            else:
                # New Vote
                CommentVote.objects.create(user=user, comment=comment, is_helpful=is_helpful)
                if is_helpful:
                    comment.helpful_count = F('helpful_count') + 1
                else:
                    comment.unhelpful_count = F('unhelpful_count') + 1
                message = "Vote added"

            comment.save()
            
            comment.refresh_from_db()

        return Response({
            'message': message,
            'helpful_count': comment.helpful_count,
            'unhelpful_count': comment.unhelpful_count
        }, status=status.HTTP_200_OK)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all().order_by('-starts_at')
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)