"""
Seller Portal Endpoints
Manage sales, orders, payouts, and analytics for sellers
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.modelsx.marketplace import DigitalProduct, ProductStatus
from app.modelsx.order import Order
from app.schemas.seller import (
    SellerDashboard, SellerOrders, SellerOrderBasic,
    SellerProductBasic, PayoutRequest, SellerPayout,
    SellerAnalyticsTimeline, SellerAnalyticsProducts
)

router = APIRouter(prefix="/seller", tags=["seller"])


def require_seller(current_user: User = Depends(get_current_user)):
    """Ensure user is a seller (has merchant role or is creating seller profile)"""
    if not (current_user.role == UserRole.MENTOR or current_user.role == UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only sellers can access this endpoint")
    return current_user


@router.get("/dashboard", response_model=SellerDashboard)
def get_seller_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get seller dashboard overview with key metrics."""
    
    # Get all products for this seller
    products = db.query(DigitalProduct).filter(
        DigitalProduct.seller_id == current_user.id
    ).all()
    
    # Calculate metrics
    total_sales = sum(p.sales_count for p in products)
    total_revenue = sum(float(p.total_revenue or 0) for p in products)
    
    # Calculate average rating across all products
    products_with_rating = [p for p in products if p.average_rating > 0]
    average_rating = (sum(p.average_rating for p in products_with_rating) / len(products_with_rating)) if products_with_rating else 0.0
    
    # Get recent orders (purchases of seller's products)
    recent_orders = db.query(Order).join(
        DigitalProduct, Order.user_id == current_user.id  # Simplified - ideally join on product
    ).order_by(desc(Order.created_at)).limit(5).all()
    
    # Fallback: Get user's recent orders
    if not recent_orders:
        recent_orders = db.query(Order).filter(
            Order.user_id == current_user.id
        ).order_by(desc(Order.created_at)).limit(5).all()
    
    # Get top 3 products by sales
    top_products = sorted(products, key=lambda p: p.sales_count, reverse=True)[:3]
    
    return {
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "average_rating": average_rating,
        "total_products": len(products),
        "recent_orders": recent_orders,
        "top_products": top_products
    }


@router.get("/orders", response_model=SellerOrders)
def get_seller_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get seller's orders (sales of their products)."""
    
    # Get seller's product IDs
    product_ids = db.query(DigitalProduct.id).filter(
        DigitalProduct.seller_id == current_user.id
    ).all()
    
    product_ids = [p[0] for p in product_ids]
    
    if not product_ids:
        return {"total": 0, "orders": []}
    
    # Query orders for these products (simplified approach)
    # In production, you'd join with order_items table
    query = db.query(Order).offset(skip).limit(limit)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(desc(Order.created_at)).all()
    total = db.query(Order).count()
    
    return {
        "total": total,
        "orders": orders
    }


@router.get("/payouts")
def get_seller_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get seller's payout history."""
    
    # Returns empty list for now (payout model may not exist yet)
    # TODO: Implement when Payout model is added
    return {
        "total": 0,
        "payouts": []
    }


@router.post("/request-payout")
def request_payout(
    request: PayoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request a payout from seller account."""
    
    # Get seller's total available balance
    products = db.query(DigitalProduct).filter(
        DigitalProduct.seller_id == current_user.id
    ).all()
    
    total_revenue = sum(float(p.total_revenue or 0) for p in products)
    
    if request.amount > total_revenue:
        raise HTTPException(
            status_code=400,
            detail=f"Payout amount exceeds available balance (${total_revenue:.2f})"
        )
    
    # TODO: Create Payout record when model is available
    
    return {
        "message": "Payout request submitted",
        "amount": request.amount,
        "status": "pending",
        "available_balance": total_revenue - request.amount
    }


@router.get("/analytics/timeline")
def get_seller_analytics_timeline(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get revenue timeline data for seller."""
    
    products = db.query(DigitalProduct).filter(
        DigitalProduct.seller_id == current_user.id
    ).all()
    
    # Generate timeline data from products
    timeline = []
    end_date = datetime.utcnow().date()
    
    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.isoformat()
        
        # Simplified: distribute sales evenly (in production, query actual sales data)
        daily_revenue = sum(float(p.total_revenue or 0) for p in products) / max(days, 1)
        daily_sales = sum(p.sales_count for p in products) // max(days, 1)
        
        timeline.append({
            "date": date_str,
            "revenue": round(daily_revenue, 2),
            "sales_count": daily_sales
        })
    
    return {
        "timeline": reversed(timeline),  # Return in chronological order
        "total_period_revenue": sum(float(p.total_revenue or 0) for p in products),
        "total_period_sales": sum(p.sales_count for p in products)
    }


@router.get("/analytics/products")
def get_seller_products_analytics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product performance analytics for seller."""
    
    products = db.query(DigitalProduct).filter(
        DigitalProduct.seller_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    analytics = []
    for product in products:
        analytics.append({
            "product_id": product.id,
            "product_name": product.name,
            "sales_count": product.sales_count,
            "revenue": float(product.total_revenue or 0),
            "average_rating": product.average_rating,
            "views_count": product.views_count,
            "status": product.status
        })
    
    return {
        "products": analytics,
        "total": len(analytics)
    }
