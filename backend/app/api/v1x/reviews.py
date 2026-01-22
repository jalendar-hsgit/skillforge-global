"""
Product Review API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.modelsx.marketplace import DigitalProduct
from app.models.modelsx.product_review import ProductReview, ReviewHelpfulVote
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse,
    ReviewDeleteResponse, ReviewHelpfulResponse, ProductRatingResponse,
    SellerResponseSchema
)
from app.core.security import get_current_user

router = APIRouter(prefix="/marketplace/products", tags=["reviews"])


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product review",
    responses={
        201: {"description": "Review created"},
        404: {"description": "Product not found"},
        400: {"description": "Invalid request"},
        401: {"description": "Not authenticated"}
    }
)
def create_review(
    product_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new review for a product.
    
    - Requires authentication
    - Product must exist
    - User can only leave one review per product (can update later)
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.reviewer_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product. Update your existing review instead."
        )
    
    # Create review
    new_review = ProductReview(
        product_id=product_id,
        reviewer_id=current_user.id,
        rating=review.rating,
        title=review.title,
        text=review.text,
        is_verified_purchase=False  # TODO: Check if user purchased this product
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    # Return response with user details
    return ReviewResponse(
        id=new_review.id,
        product_id=new_review.product_id,
        reviewer_id=new_review.reviewer_id,
        reviewer_name=current_user.name,
        reviewer_avatar=current_user.avatar_url,
        rating=new_review.rating,
        title=new_review.title,
        text=new_review.text,
        is_verified_purchase=new_review.is_verified_purchase,
        is_approved=new_review.is_approved,
        helpful_count=new_review.helpful_count,
        unhelpful_count=new_review.unhelpful_count,
        seller_response=new_review.seller_response,
        seller_response_at=new_review.seller_response_at,
        created_at=new_review.created_at,
        updated_at=new_review.updated_at
    )


@router.get(
    "/{product_id}/reviews",
    response_model=ReviewListResponse,
    summary="Get product reviews",
    responses={
        200: {"description": "Reviews returned"},
        404: {"description": "Product not found"}
    }
)
def get_reviews(
    product_id: int,
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(10, gt=0, le=100, description="Items to return"),
    sort_by: str = Query("newest", description="Sort by: newest, oldest, helpful, rating_high, rating_low"),
    rating_filter: int = Query(None, ge=1, le=5, description="Filter by rating (1-5)"),
    verified_only: bool = Query(False, description="Only verified purchase reviews"),
    db: Session = Depends(get_db)
):
    """
    Get reviews for a product with pagination and filtering.
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Build query
    query = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    )
    
    # Apply filters
    if rating_filter:
        query = query.filter(ProductReview.rating == rating_filter)
    if verified_only:
        query = query.filter(ProductReview.is_verified_purchase == True)
    
    # Get total before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(desc(ProductReview.created_at))
    elif sort_by == "oldest":
        query = query.order_by(ProductReview.created_at)
    elif sort_by == "helpful":
        query = query.order_by(desc(ProductReview.helpful_count))
    elif sort_by == "rating_high":
        query = query.order_by(desc(ProductReview.rating))
    elif sort_by == "rating_low":
        query = query.order_by(ProductReview.rating)
    
    # Apply pagination
    reviews = query.offset(skip).limit(limit).all()
    
    # Build responses with user details
    review_responses = []
    for review in reviews:
        reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
        review_responses.append(ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            reviewer_id=review.reviewer_id,
            reviewer_name=reviewer.name if reviewer else "Anonymous",
            reviewer_avatar=reviewer.avatar_url if reviewer else None,
            rating=review.rating,
            title=review.title,
            text=review.text,
            is_verified_purchase=review.is_verified_purchase,
            is_approved=review.is_approved,
            helpful_count=review.helpful_count,
            unhelpful_count=review.unhelpful_count,
            seller_response=review.seller_response,
            seller_response_at=review.seller_response_at,
            created_at=review.created_at,
            updated_at=review.updated_at
        ))
    
    # Calculate rating distribution
    all_reviews = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).all()
    
    rating_dist = {str(i): 0 for i in range(1, 6)}
    avg_rating = 0.0
    
    if all_reviews:
        for r in all_reviews:
            rating_dist[str(r.rating)] += 1
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    
    return ReviewListResponse(
        reviews=review_responses,
        total=total,
        skip=skip,
        limit=limit,
        average_rating=round(avg_rating, 1),
        rating_distribution=rating_dist
    )


@router.put(
    "/{product_id}/reviews/{review_id}",
    response_model=ReviewResponse,
    summary="Update product review",
    responses={
        200: {"description": "Review updated"},
        404: {"description": "Review or product not found"},
        403: {"description": "Not review owner"},
        401: {"description": "Not authenticated"}
    }
)
def update_review(
    product_id: int,
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing review.
    
    - Only review owner can update
    - Can modify rating, title, or text
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get review
    review = db.query(ProductReview).filter(
        ProductReview.id == review_id,
        ProductReview.product_id == product_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Update fields
    if review_update.rating:
        review.rating = review_update.rating
    if review_update.title:
        review.title = review_update.title
    if review_update.text:
        review.text = review_update.text
    
    review.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        reviewer_id=review.reviewer_id,
        reviewer_name=current_user.name,
        reviewer_avatar=current_user.avatar_url,
        rating=review.rating,
        title=review.title,
        text=review.text,
        is_verified_purchase=review.is_verified_purchase,
        is_approved=review.is_approved,
        helpful_count=review.helpful_count,
        unhelpful_count=review.unhelpful_count,
        seller_response=review.seller_response,
        seller_response_at=review.seller_response_at,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.delete(
    "/{product_id}/reviews/{review_id}",
    response_model=ReviewDeleteResponse,
    summary="Delete product review",
    responses={
        200: {"description": "Review deleted"},
        404: {"description": "Review or product not found"},
        403: {"description": "Not review owner or admin"},
        401: {"description": "Not authenticated"}
    }
)
def delete_review(
    product_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a review.
    
    - Only review owner or admin can delete
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get review
    review = db.query(ProductReview).filter(
        ProductReview.id == review_id,
        ProductReview.product_id == product_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership (owner or admin/seller)
    from app.models.user import UserRole
    is_owner = review.reviewer_id == current_user.id
    is_seller = product.seller_id == current_user.id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    if not (is_owner or is_seller or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this review"
        )
    
    db.delete(review)
    db.commit()
    
    return ReviewDeleteResponse(
        success=True,
        message="Review deleted successfully"
    )


@router.post(
    "/{product_id}/reviews/{review_id}/helpful",
    response_model=ReviewHelpfulResponse,
    summary="Mark review as helpful/unhelpful",
    responses={
        200: {"description": "Vote recorded"},
        404: {"description": "Review or product not found"},
        401: {"description": "Not authenticated"}
    }
)
def toggle_helpful_vote(
    product_id: int,
    review_id: int,
    is_helpful: bool = Query(..., description="True for helpful, False for unhelpful"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a review as helpful or unhelpful.
    
    - User can change their vote by voting again
    - Voting is anonymous (tracked by user_id but not displayed)
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get review
    review = db.query(ProductReview).filter(
        ProductReview.id == review_id,
        ProductReview.product_id == product_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check for existing vote
    existing_vote = db.query(ReviewHelpfulVote).filter(
        ReviewHelpfulVote.review_id == review_id,
        ReviewHelpfulVote.user_id == current_user.id
    ).first()
    
    # Update counts if changing vote
    if existing_vote:
        if existing_vote.is_helpful:
            review.helpful_count = max(0, review.helpful_count - 1)
        else:
            review.unhelpful_count = max(0, review.unhelpful_count - 1)
        db.delete(existing_vote)
    
    # Add new vote
    if existing_vote and existing_vote.is_helpful == is_helpful:
        # User is toggling off their vote
        pass
    else:
        # Add new vote
        vote = ReviewHelpfulVote(
            review_id=review_id,
            user_id=current_user.id,
            is_helpful=is_helpful
        )
        db.add(vote)
        
        # Update counts
        if is_helpful:
            review.helpful_count += 1
        else:
            review.unhelpful_count += 1
    
    db.commit()
    db.refresh(review)
    
    # Get current user's vote
    current_vote = db.query(ReviewHelpfulVote).filter(
        ReviewHelpfulVote.review_id == review_id,
        ReviewHelpfulVote.user_id == current_user.id
    ).first()
    
    return ReviewHelpfulResponse(
        review_id=review_id,
        helpful_count=review.helpful_count,
        unhelpful_count=review.unhelpful_count,
        user_vote=current_vote.is_helpful if current_vote else None
    )


@router.get(
    "/{product_id}/rating",
    response_model=ProductRatingResponse,
    summary="Get product rating summary",
    responses={
        200: {"description": "Rating summary returned"},
        404: {"description": "Product not found"}
    }
)
def get_product_rating(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the rating summary for a product.
    
    Returns:
    - Average rating
    - Total reviews
    - Rating distribution (count for each star rating)
    - Verified purchase review count
    """
    # Verify product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get all approved reviews
    reviews = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).all()
    
    # Calculate stats
    rating_dist = {str(i): 0 for i in range(1, 6)}
    avg_rating = 0.0
    verified_count = 0
    
    if reviews:
        for review in reviews:
            rating_dist[str(review.rating)] += 1
            if review.is_verified_purchase:
                verified_count += 1
        
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    return ProductRatingResponse(
        product_id=product_id,
        average_rating=round(avg_rating, 1),
        total_reviews=len(reviews),
        rating_distribution=rating_dist,
        verified_reviews=verified_count
    )
