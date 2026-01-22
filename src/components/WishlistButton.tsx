import { useState, useEffect } from 'react';
import { Heart, HeartOff, Loader2 } from 'lucide-react';

interface WishlistButtonProps {
  productId: number;
  productName?: string;
  variant?: 'icon' | 'button';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onToggle?: (inWishlist: boolean) => void;
}

export default function WishlistButton({
  productId,
  productName = 'Product',
  variant = 'icon',
  size = 'md',
  className = '',
  onToggle
}: WishlistButtonProps) {
  const [inWishlist, setInWishlist] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(true);

  // Check if product is in wishlist on mount
  useEffect(() => {
    checkWishlistStatus();
  }, [productId]);

  const checkWishlistStatus = async () => {
    try {
      setCheckingStatus(true);
      const token = localStorage.getItem('token');
      if (!token) {
        setCheckingStatus(false);
        return;
      }

      const response = await fetch(
        `http://localhost:8001/api/v1x/marketplace/wishlist/check/${productId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setInWishlist(data.in_wishlist);
      }
    } catch (error) {
      console.error('Error checking wishlist status:', error);
    } finally {
      setCheckingStatus(false);
    }
  };

  const toggleWishlist = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please login to manage your wishlist');
      return;
    }

    try {
      setLoading(true);

      if (inWishlist) {
        // Remove from wishlist
        const response = await fetch(
          `http://localhost:8001/api/v1x/marketplace/wishlist/${productId}`,
          {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.ok) {
          setInWishlist(false);
          onToggle?.(false);
        } else {
          alert('Failed to remove from wishlist');
        }
      } else {
        // Add to wishlist
        const response = await fetch(
          'http://localhost:8001/api/v1x/marketplace/wishlist',
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId })
          }
        );

        if (response.ok) {
          setInWishlist(true);
          onToggle?.(true);
        } else if (response.status === 400) {
          // Already in wishlist
          setInWishlist(true);
        } else {
          alert('Failed to add to wishlist');
        }
      }
    } catch (error) {
      console.error('Error toggling wishlist:', error);
      alert('Error updating wishlist');
    } finally {
      setLoading(false);
    }
  };

  if (checkingStatus) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <Loader2 className={`animate-spin text-gray-400 ${
          size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'
        }`} />
      </div>
    );
  }

  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const buttonSizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-5 py-3 text-lg'
  };

  if (variant === 'icon') {
    return (
      <button
        onClick={toggleWishlist}
        disabled={loading}
        className={`transition-colors hover:text-red-500 ${className} ${
          loading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        title={inWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
      >
        {inWishlist ? (
          <Heart className={`${sizeClasses[size]} fill-red-500 text-red-500`} />
        ) : (
          <Heart className={`${sizeClasses[size]}`} />
        )}
      </button>
    );
  }

  return (
    <button
      onClick={toggleWishlist}
      disabled={loading}
      className={`${buttonSizeClasses[size]} rounded-lg font-medium transition-all
        ${inWishlist
          ? 'bg-red-100 text-red-600 hover:bg-red-200'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }
        ${loading ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      <div className="flex items-center gap-2">
        {inWishlist ? (
          <Heart className={`${sizeClasses[size]} fill-red-500`} />
        ) : (
          <Heart className={sizeClasses[size]} />
        )}
        <span>{inWishlist ? 'Saved' : 'Save'}</span>
      </div>
    </button>
  );
}
