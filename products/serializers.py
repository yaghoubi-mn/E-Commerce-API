from rest_framework import serializers
from products.models import Category, CommentVote, Discount, Product, Cart, Comment


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
    

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'id', 'title', 'discount_type', 'code', 'description', 
            'discount_type', 'value', 'min_purchase', 'max_discount', 
            'usage_limit_total', 'usage_limit_per_user', 'used_count', 
            'applies_to', 'target_ids', 'is_active', 'starts_at', 'ends_at', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Check that start date is before end date.
        Check that percentage discounts don't exceed 100%.
        """
        # 1. Date Validation
        start = data.get('starts_at', self.instance.starts_at if self.instance else None)
        end = data.get('ends_at', self.instance.ends_at if self.instance else None)

        if start and end and start > end:
            raise serializers.ValidationError({"ends_at": "End date must be after start date."})

        # 2. Value Validation
        d_type = data.get('discount_type', self.instance.discount_type if self.instance else None)
        value = data.get('value', self.instance.value if self.instance else None)

        if d_type == 'percentage' and value and value > 100:
             raise serializers.ValidationError({"value": "Percentage discount cannot exceed 100%."})

        return data