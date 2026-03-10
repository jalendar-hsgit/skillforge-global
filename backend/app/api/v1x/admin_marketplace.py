"""
Admin Marketplace Endpoints
Manage marketplace revenue, payouts, and refunds
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, desc, asc
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.db import get_db
from app.core.rbac import require_admin
from app.models.user import User
from app.modelsx.marketplace import DigitalProduct
from app.modelsx.order import Order

router = APIRouter(prefix="/admin/marketplace", tags=["admin-marketplace"])


# ============================================================================
# REVENUE ENDPOINTS
# ============================================================================

@router.get("/revenue")
def get_total_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get total platform revenue and metrics.
    
    Returns:
        - total_revenue: Total revenue from all sales
        - total_orders: Total number of orders
        - total_sellers: Number of active sellers
        - total_products: Total products on platform
        - average_order_value: Average order amount
        - refund_amount: Total refunded amount
    """
    
    # Get all orders
    all_orders = db.query(Order).filter(
        Order.status.in_(["completed", "pending", "refunded"])
    ).all()
    
    # Calculate metrics
    completed_orders = [o for o in all_orders if o.status == "completed"]
    refunded_orders = [o for o in all_orders if o.status == "refunded"]
    
    total_revenue = sum(float(o.amount) for o in completed_orders)
    refund_amount = sum(float(o.amount) for o in refunded_orders)
    net_revenue = total_revenue - refund_amount
    
    average_order = (total_revenue / len(completed_orders)) if completed_orders else 0
    
    # Get seller and product counts
    total_sellers = db.query(func.count(DigitalProduct.seller_id.distinct())).scalar() or 0
    total_products = db.query(func.count(DigitalProduct.id)).scalar() or 0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "net_revenue": round(net_revenue, 2),
        "refund_amount": round(refund_amount, 2),
        "total_orders": len(completed_orders),
        "pending_orders": len([o for o in all_orders if o.status == "pending"]),
        "refunded_orders": len(refunded_orders),
        "total_sellers": total_sellers,
        "total_products": total_products,
        "average_order_value": round(average_order, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/revenue-by-seller")
def get_revenue_by_seller(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("revenue", regex="^(revenue|orders|rating)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get revenue breakdown by seller.
    
    Query Params:
        - skip: Pagination offset
        - limit: Results per page
        - sort_by: Sort field (revenue, orders, rating)
    
    Returns:
        - sellers: List of seller revenue details
        - total: Total number of sellers
    """
    
    # Get all sellers with their products
    sellers_data = []
    
    sellers = db.query(DigitalProduct.seller_id).distinct().all()
    sellers_list = [s[0] for s in sellers]
    
    for seller_id in sellers_list:
        products = db.query(DigitalProduct).filter(
            DigitalProduct.seller_id == seller_id
        ).all()
        
        # Calculate seller metrics
        total_sales = sum(p.sales_count for p in products)
        total_revenue = sum(float(p.total_revenue or 0) for p in products)
        avg_rating = (sum(p.average_rating for p in products) / len(products)) if products else 0
        
        # Get seller user info
        seller_user = db.query(User).filter(User.id == seller_id).first()
        
        sellers_data.append({
            "seller_id": seller_id,
            "seller_name": seller_user.email if seller_user else "Unknown",
            "seller_email": seller_user.email if seller_user else "Unknown",
            "total_products": len(products),
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "average_rating": round(avg_rating, 2),
            "active": True
        })
    
    # Sort results
    if sort_by == "revenue":
        sellers_data.sort(key=lambda x: x["total_revenue"], reverse=True)
    elif sort_by == "orders":
        sellers_data.sort(key=lambda x: x["total_sales"], reverse=True)
    elif sort_by == "rating":
        sellers_data.sort(key=lambda x: x["average_rating"], reverse=True)
    
    # Paginate
    total = len(sellers_data)
    paginated = sellers_data[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "sellers": paginated
    }


# ============================================================================
# PAYOUT ENDPOINTS
# ============================================================================

@router.get("/payouts")
def get_payout_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    seller_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get payout management view for all sellers or specific seller.
    
    Query Params:
        - skip: Pagination offset
        - limit: Results per page
        - seller_id: Filter by seller (optional)
        - status: Filter by payout status (pending, processing, completed, failed)
    
    Returns:
        - payouts: List of payout records
        - total: Total number of payouts
    """
    
    # TODO: This requires a Payout model integration
    # For now, return framework structure
    
    payouts_data = []
    
    # Get sellers with pending payments
    sellers = db.query(DigitalProduct.seller_id).distinct().all()
    sellers_list = [s[0] for s in sellers]
    
    if seller_id:
        sellers_list = [seller_id] if seller_id in sellers_list else []
    
    for sid in sellers_list:
        products = db.query(DigitalProduct).filter(
            DigitalProduct.seller_id == sid
        ).all()
        
        total_revenue = sum(float(p.total_revenue or 0) for p in products)
        seller_user = db.query(User).filter(User.id == sid).first()
        
        # Simulate payout records (would be from Payout model)
        if total_revenue > 0:
            payouts_data.append({
                "id": sid,  # Simplified
                "seller_id": sid,
                "seller_email": seller_user.email if seller_user else "Unknown",
                "amount": round(total_revenue, 2),
                "status": status or "pending",
                "request_date": datetime.utcnow().isoformat(),
                "processed_date": None,
                "payment_method": "bank_transfer"
            })
    
    # Filter by status if provided
    if status:
        payouts_data = [p for p in payouts_data if p["status"] == status]
    
    # Paginate
    total = len(payouts_data)
    paginated = payouts_data[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "payouts": paginated
    }


@router.post("/process-payout")
def process_payout(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Process payout for a seller.
    
    Request Body:
        {
            "seller_id": 123,
            "amount": 500.00,
            "payment_method": "stripe_connect" or "bank_transfer"
        }
    
    Returns:
        - success: Whether payout was processed
        - payout_id: ID of processed payout
        - amount: Payout amount
        - status: New payout status
    """
    
    seller_id = request_data.get("seller_id")
    amount = request_data.get("amount")
    payment_method = request_data.get("payment_method", "bank_transfer")
    
    if not seller_id or not amount:
        raise HTTPException(status_code=400, detail="seller_id and amount required")
    
    # Verify seller exists
    seller = db.query(User).filter(User.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Verify amount is reasonable
    products = db.query(DigitalProduct).filter(
        DigitalProduct.seller_id == seller_id
    ).all()
    total_revenue = sum(float(p.total_revenue or 0) for p in products)
    
    if amount > total_revenue:
        raise HTTPException(
            status_code=400,
            detail=f"Payout amount exceeds available balance (${total_revenue:.2f})"
        )
    
    # TODO: Process actual payout via Stripe/PayPal based on payment_method
    # For now, return success response
    
    return {
        "success": True,
        "payout_id": f"payout_{seller_id}_{int(datetime.utcnow().timestamp())}",
        "seller_id": seller_id,
        "seller_email": seller.email,
        "amount": round(amount, 2),
        "status": "processing",
        "payment_method": payment_method,
        "processed_at": datetime.utcnow().isoformat(),
        "message": "Payout initiated successfully"
    }


# ============================================================================
# REFUND ENDPOINTS
# ============================================================================

@router.get("/refunds")
def get_refund_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    seller_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get refund tracking and management.
    
    Query Params:
        - skip: Pagination offset
        - limit: Results per page
        - status: Filter by refund status (pending, approved, rejected, completed)
        - seller_id: Filter by affected seller
    
    Returns:
        - refunds: List of refund records
        - total: Total number of refunds
    """
    
    # Get refunded orders
    refunded_orders = db.query(Order).filter(
        Order.status == "refunded"
    ).all()
    
    refunds_data = []
    
    for order in refunded_orders:
        seller_info = "Multiple"  # Orders can have multiple sellers
        
        refunds_data.append({
            "id": order.id,
            "order_id": order.order_number,
            "user_id": order.user_id,
            "amount": float(order.amount),
            "discount_recovered": float(order.discount_amount),
            "net_refunded": float(order.amount - order.discount_amount),
            "status": "completed",
            "refund_reason": "Customer request",  # Would come from refund model
            "refund_date": order.updated_at.isoformat(),
            "processed_by": "System"
        })
    
    # Filter by status if provided
    if status:
        refunds_data = [r for r in refunds_data if r["status"] == status]
    
    # Paginate
    total = len(refunds_data)
    paginated = refunds_data[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "refunds": paginated,
        "total_refunded": round(sum(r["net_refunded"] for r in refunds_data), 2)
    }


# ============================================================================
# ANALYTICS & INSIGHTS
# ============================================================================

@router.get("/analytics/summary")
def get_marketplace_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get marketplace analytics summary for given period.
    
    Query Params:
        - days: Number of days to analyze (1-365)
    
    Returns:
        - period_revenue: Revenue in period
        - period_orders: Orders in period
        - period_sellers: Active sellers in period
        - growth_rate: Revenue growth vs previous period
        - top_sellers: Top 5 sellers by revenue
        - top_products: Top 5 products by sales
    """
    
    all_orders = db.query(Order).filter(
        Order.status == "completed"
    ).all()
    
    period_orders = [o for o in all_orders if o.created_at and (datetime.utcnow() - o.created_at).days <= days]
    period_revenue = sum(float(o.amount) for o in period_orders)
    
    # Get top sellers
    sellers_dict = {}
    for order in period_orders:
        if order.user_id not in sellers_dict:
            sellers_dict[order.user_id] = 0
        sellers_dict[order.user_id] += float(order.amount)
    
    top_sellers = sorted(sellers_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Get top products
    products = db.query(DigitalProduct).order_by(
        desc(DigitalProduct.sales_count)
    ).limit(5).all()
    
    return {
        "period_days": days,
        "period_revenue": round(period_revenue, 2),
        "period_orders": len(period_orders),
        "period_sellers": len(sellers_dict),
        "average_order_value": round(period_revenue / len(period_orders), 2) if period_orders else 0,
        "top_sellers": [
            {"seller_id": sid, "revenue": round(rev, 2)} 
            for sid, rev in top_sellers
        ],
        "top_products": [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sales": p.sales_count,
                "revenue": round(float(p.total_revenue or 0), 2)
            }
            for p in products
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
