"""
Wishlist API Endpoints - User wishlist management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.modelsx.marketplace import DigitalProduct
from app.models.modelsx.wishlist import Wishlist
from app.schemas.wishlist import (
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistListResponse,
    WishlistCountResponse,
    WishlistDeleteResponse,
    WishlistCheckResponse
)
from app.core.security import get_current_user

router = APIRouter(prefix="/marketplace/wishlist", tags=["wishlist"])


@router.post(
    "",
    response_model=WishlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add product to wishlist",
    responses={
        201: {"description": "Product added to wishlist"},
        400: {"description": "Product already in wishlist"},
        404: {"description": "Product not found"},
        401: {"description": "Not authenticated"}
    }
)
def add_to_wishlist(
    item: WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a product to the user's wishlist.
    
    - Requires authentication
    - Product must exist
    - Each product can only be added once per user
    """
    # Check if product exists
    product = db.query(DigitalProduct).filter(DigitalProduct.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == item.product_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in your wishlist"
        )
    
    # Create wishlist item
    wishlist_item = Wishlist(
        user_id=current_user.id,
        product_id=item.product_id
    )
    
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    
    # Build response with product details
    return WishlistItemResponse(
        id=wishlist_item.id,
        user_id=wishlist_item.user_id,
        product_id=wishlist_item.product_id,
        created_at=wishlist_item.created_at,
        product_name=product.name,
        product_slug=product.slug,
        product_price=product.price,
        product_type=product.product_type,
        product_status=product.status,
        seller_id=product.seller_id,
        seller_name=product.seller.name if product.seller else None
    )


@router.get(
    "",
    response_model=WishlistListResponse,
    summary="Get user's wishlist",
    responses={
        200: {"description": "Wishlist items returned"},
        401: {"description": "Not authenticated"}
    }
)
def get_wishlist(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(20, gt=0, le=100, description="Items to return"),
    sort_by: str = Query("newest", description="Sort by: newest, oldest, price_low, price_high"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the user's wishlist with pagination and sorting.
    
    Supports sorting:
    - newest: Recently added items first
    - oldest: Oldest items first
    - price_low: Lowest price first
    - price_high: Highest price first
    """
    # Base query
    query = db.query(Wishlist).filter(Wishlist.user_id == current_user.id)
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(Wishlist.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Wishlist.created_at.asc())
    elif sort_by == "price_low":
        query = query.join(DigitalProduct).order_by(DigitalProduct.price.asc())
    elif sort_by == "price_high":
        query = query.join(DigitalProduct).order_by(DigitalProduct.price.desc())
    else:
        query = query.order_by(Wishlist.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    wishlist_items = query.offset(skip).limit(limit).all()
    
    # Build response with product details
    items = []
    for item in wishlist_items:
        product = item.product
        items.append(WishlistItemResponse(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            created_at=item.created_at,
            product_name=product.name,
            product_slug=product.slug,
            product_price=product.price,
            product_type=product.product_type,
            product_status=product.status,
            seller_id=product.seller_id,
            seller_name=product.seller.name if product.seller else None
        ))
    
    return WishlistListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/count",
    response_model=WishlistCountResponse,
    summary="Get wishlist item count",
    responses={
        200: {"description": "Wishlist count returned"},
        401: {"description": "Not authenticated"}
    }
)
def get_wishlist_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the count of items in the user's wishlist.
    """
    count = db.query(func.count(Wishlist.id)).filter(
        Wishlist.user_id == current_user.id
    ).scalar() or 0
    
    return WishlistCountResponse(
        count=count,
        user_id=current_user.id
    )


@router.delete(
    "/{product_id}",
    response_model=WishlistDeleteResponse,
    summary="Remove product from wishlist",
    responses={
        200: {"description": "Product removed from wishlist"},
        404: {"description": "Item not in wishlist"},
        401: {"description": "Not authenticated"}
    }
)
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a product from the user's wishlist.
    
    - Requires authentication
    - User must be the owner of the wishlist item
    """
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in wishlist"
        )
    
    db.delete(wishlist_item)
    db.commit()
    
    return WishlistDeleteResponse(
        success=True,
        message="Product removed from wishlist",
        product_id=product_id
    )


@router.get(
    "/check/{product_id}",
    response_model=WishlistCheckResponse,
    summary="Check if product is in wishlist",
    responses={
        200: {"description": "Wishlist status returned"},
        401: {"description": "Not authenticated"}
    }
)
def check_in_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a product is in the user's wishlist.
    """
    exists = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first() is not None
    
    return WishlistCheckResponse(
        in_wishlist=exists,
        product_id=product_id
    )
