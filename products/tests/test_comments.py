import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from products.models import Product, Comment, CommentVote, User


@pytest.fixture
def comment(user, product):
    return Comment.objects.create(
        user=user,
        product=product,
        rating=5,
        content="Great stuff",
        is_approved=True # Start approved for read tests
    )


@pytest.mark.django_db
class TestCreateComment:
    
    def test_create_comment_authenticated(self, authenticated_client, user, product):
        """Valid user can create a comment."""
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        data = {'rating': 5, 'content': 'Amazing!'}
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1
        assert Comment.objects.get().user == user
        # ensure default state is unapproved
        assert Comment.objects.get().is_approved is False

    def test_create_comment_unauthenticated(self, api_client, product):
        """Anon user cannot create comment."""
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        data = {'rating': 5, 'content': 'Bot spam'}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_invalid_rating(self, authenticated_client, product):
        """Rating must be 1-5."""
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        
        # Test > 5
        response = authenticated_client.post(url, {'rating': 6, 'content': 'Bad'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test < 1
        response = authenticated_client.post(url, {'rating': 0, 'content': 'Bad'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_security_mass_assignment(self, authenticated_client, product):
        """User cannot verify their own purchase or approve own comment via API."""
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        
        # Malicious payload
        data = {
            'rating': 5, 
            'content': 'Hacked',
            'is_approved': True, 
            'is_verified_purchase': True,
            'helpful_count': 1000
        }
        
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        comment = Comment.objects.get()
        # Assert fields were ignored
        assert comment.is_approved is False
        assert comment.is_verified_purchase is False
        assert comment.helpful_count == 0


@pytest.mark.django_db
class TestListComments:
    
    def test_list_comments_hides_unapproved(self, api_client, product, user):
        """Only approved comments should appear in the list."""
        # Create 1 approved, 1 unapproved
        Comment.objects.create(user=user, product=product, content="Approve Me", rating=5, is_approved=True)
        Comment.objects.create(user=user, product=product, content="Hide Me", rating=1, is_approved=False)
        
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['content'] == "Approve Me"

    def test_list_comments_filters_by_product(self, api_client, product, product_two, user):
        """Should not see comments from other products."""
        
        Comment.objects.create(user=user, product=product_two, content="Wrong Product", rating=5, is_approved=True)
        
        url = reverse('product-comments-list', kwargs={'product_id': product.id})
        response = api_client.get(url)
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestUpdateDeleteComment:

    def test_update_comment_owner(self, authenticated_client, comment):
        """Owner can edit. Should reset is_approved to False."""
        url = reverse('comment-detail', kwargs={'comment_id': comment.id})
        data = {'rating': 4, 'content': 'Changed my mind'}
        
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == 'Changed my mind'
        # Security check: content change requires re-approval
        assert comment.is_approved is False 

    def test_update_comment_not_owner(self, api_client, user_two, comment):
        """Another user cannot edit your comment."""
        api_client.force_authenticate(user=user_two)
        url = reverse('comment-detail', kwargs={'comment_id': comment.id})
        data = {'rating': 1, 'content': 'Hacked'}
        
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_owner(self, authenticated_client, comment):
        """Owner can delete."""
        url = reverse('comment-detail', kwargs={'comment_id': comment.id})
        
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0


@pytest.mark.django_db
class TestVoting:

    def test_upvote_new(self, api_client, user_two, comment):
        """New upvote increases count and creates vote record."""
        api_client.force_authenticate(user=user_two)
        url = reverse('comment-upvote', kwargs={'comment_id': comment.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.helpful_count == 1
        assert comment.unhelpful_count == 0
        assert CommentVote.objects.filter(user=user_two, comment=comment, is_helpful=True).exists()

    def test_upvote_toggle_off(self, api_client, user_two, comment):
        """Upvoting twice removes the vote."""
        api_client.force_authenticate(user=user_two)
        url = reverse('comment-upvote', kwargs={'comment_id': comment.id})
        
        # First Vote
        api_client.post(url)
        
        # Second Vote (Same endpoint)
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "Vote removed"
        
        comment.refresh_from_db()
        assert comment.helpful_count == 0
        assert not CommentVote.objects.filter(user=user_two, comment=comment).exists()

    def test_switch_up_to_down(self, api_client, user_two, comment):
        """Switching from Up to Down updates both counters correctly."""
        api_client.force_authenticate(user=user_two)
        up_url = reverse('comment-upvote', kwargs={'comment_id': comment.id})
        down_url = reverse('comment-downvote', kwargs={'comment_id': comment.id})
        
        # 1. Cast Upvote
        api_client.post(up_url) 
        comment.refresh_from_db()
        assert comment.helpful_count == 1
        
        # 2. Cast Downvote (Switch)
        response = api_client.post(down_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "Vote changed"
        
        comment.refresh_from_db()
        # Helpful should go 1 -> 0
        assert comment.helpful_count == 0
        # Unhelpful should go 0 -> 1
        assert comment.unhelpful_count == 1
        
        vote = CommentVote.objects.get(user=user_two, comment=comment)
        assert vote.is_helpful is False

    def test_vote_unauthenticated(self, api_client, comment):
        url = reverse('comment-upvote', kwargs={'comment_id': comment.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED