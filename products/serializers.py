from rest_framework import serializers
from products.models import Category, CommentVote, Product, Cart, Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = "__all__"


class CommentReadSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user_name', 'rating', 'content', 
            'is_verified_purchase', 'helpful_count', 'unhelpful_count', 
            'reply_to', 'created_at', 'updated_at'
        ]

class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['rating', 'content']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentVote
        fields = ['comment', 'is_helpful']

    def validate_comment(self, value):
        # Security: Prevent voting on your own comment
        user = self.context['request'].user
        if value.user == user:
            raise serializers.ValidationError("You cannot vote on your own comment.")
        return value
    