import { apiPost, apiGet } from './api';

export interface CreateOrderRequest {
  course_id: number;
  payment_method: string;
}

export interface CreatePaymentIntentRequest {
  order_id: number;
}

export interface ConfirmPaymentRequest {
  order_id: number;
  payment_intent_id: string;
  payment_method_id?: string;
}

export interface OrderResponse {
  success: boolean;
  data: {
    id: number;
    user_id: number;
    course_id: number;
    order_number: string;
    amount: number;
    currency: string;
    status: string;
    payment_status: string;
    payment_id?: string;
    created_at: string;
  };
  message: string;
}

export interface PaymentIntentResponse {
  success: boolean;
  data: {
    payment_intent_id: string;
    client_secret: string;
    amount: number;
    currency: string;
  };
  message: string;
}

export interface ConfirmPaymentResponse {
  success: boolean;
  data: {
    order_id: number;
    status: string;
    payment_status: string;
    message: string;
  };
  message: string;
}

export async function createOrder(courseId: number, paymentMethod: string = 'stripe'): Promise<OrderResponse> {
  return apiPost('/api/v1x/orders/create', {
    course_id: courseId,
    payment_method: paymentMethod
  });
}

export async function createPaymentIntent(orderId: number): Promise<PaymentIntentResponse> {
  return apiPost('/api/v1x/orders/create-payment-intent', {
    order_id: orderId
  });
}

export async function confirmPayment(
  orderId: number,
  paymentIntentId: string,
  paymentMethodId?: string
): Promise<ConfirmPaymentResponse> {
  return apiPost('/api/v1x/orders/confirm-payment', {
    order_id: orderId,
    payment_intent_id: paymentIntentId,
    payment_method_id: paymentMethodId
  });
}

export async function getMyOrders(page: number = 1, pageSize: number = 10) {
  return apiGet(`/api/v1x/orders/my-orders?page=${page}&page_size=${pageSize}`);
}

export async function getOrderDetails(orderId: number) {
  return apiGet(`/api/v1x/orders/${orderId}`);
}
