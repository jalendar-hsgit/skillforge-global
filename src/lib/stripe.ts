import { loadStripe } from '@stripe/stripe-js';

// Get Stripe public key from environment
const stripePublicKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_51SkcWEBydMsdVDYvDjEH5cNq0BO8VbYGcTq64NdlpvxFwaGaaaUIrKDFrTAAV4TrNYAAz3JdOvRFcDz8PWQLBc3K00kQDXwyCd';

let stripePromise: ReturnType<typeof loadStripe>;

export const getStripe = async () => {
  if (!stripePromise) {
    stripePromise = loadStripe(stripePublicKey);
  }
  return stripePromise;
};
