# PHASE 3: PAYMENT SYSTEM & QUIZ - IMPLEMENTATION GUIDES

**Timeline**: Weeks 2-3  
**Total Duration**: 24 hours combined

---

## 📌 GUIDE 1: PAYMENT SYSTEM (12 hours)

### Overview
Full Stripe integration for mentor payments and session booking

### Feature 1: Stripe Account Setup & Integration (3 hours)

**Backend Setup**:
```
1. Create Stripe account
   - Go to https://stripe.com
   - Create test account
   - Get API keys (publishable + secret)

2. Store keys in .env
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...

3. Install stripe library
   pip install stripe

4. Backend initialization (backend/app/core/config.py)
   - Add stripe keys
   - Add webhook secret
```

**Tasks**:
```
BACKEND (3 hours):
- [ ] Install stripe library
- [ ] Add Stripe keys to config
- [ ] Create payment intent endpoint
- [ ] Create webhook endpoint
- [ ] Setup error handling for Stripe
- [ ] Add payment logging
```

### Feature 2: Booking with Payment (4 hours)

**File**: Enhance `src/pages/booking.tsx`

**Flow**:
```
1. Student selects mentor & time
2. Click "Book Session"
3. Show payment form (Stripe Card Element)
4. Student enters card details
5. System creates payment intent
6. Stripe processes payment
7. Booking confirmed
8. Payment recorded
```

**Endpoints Needed**:
```
POST /api/v1x/payments/intent
  - Create payment intent
  - Calculate amount (mentor rate × duration)
  - Return clientSecret

POST /api/v1x/payments/confirm
  - Confirm payment
  - Create booking
  - Send confirmations

POST /api/v1x/webhooks/stripe
  - Webhook for payment events
  - Update payment status
  - Handle failures
```

**Tasks**:
```
BACKEND (2 hours):
- [ ] Create payment intent endpoint
- [ ] Add payment confirmation logic
- [ ] Connect to booking creation
- [ ] Add webhook handling
- [ ] Add payment logging

FRONTEND (2 hours):
- [ ] Install @stripe/react-stripe-js
- [ ] Create payment form component
- [ ] Handle card input
- [ ] Show loading state during payment
- [ ] Show success/error messages
- [ ] Store payment method (optional)
```

### Feature 3: Mentor Payout System (3 hours)

**What to Build**:
```
Payout Dashboard
├─ Current balance
├─ Pending payouts
├─ Payout history
└─ Bank account details

Payout Logic
├─ Calculate earnings (sessions × rate - fees)
├─ Platform takes 20% fee
├─ Process weekly/monthly
├─ Direct deposit to bank

Payout History
├─ Date payout sent
├─ Amount paid
├─ Status (pending/sent/failed)
└─ View details
```

**Endpoints**:
```
GET /api/v1x/payouts/balance
GET /api/v1x/payouts/history
POST /api/v1x/payouts/request
PATCH /api/v1x/payouts/{id}/bank-account
```

**Tasks**:
```
BACKEND (2 hours):
- [ ] Create payout calculation logic
- [ ] Create payout request endpoint
- [ ] Add bank account management
- [ ] Add payout history endpoint
- [ ] Integrate with Stripe Connect

FRONTEND (1 hour):
- [ ] Display balance on mentor dashboard
- [ ] Show payout history
- [ ] Allow bank account updates
- [ ] Request payout button
```

### Feature 4: Payment History & Invoices (2 hours)

**Student View**:
```
Payment History
├─ Date
├─ Mentor name
├─ Session type
├─ Amount paid
├─ Status
└─ Receipt/Invoice button
```

**Mentor View**:
```
Earnings History
├─ Date
├─ Student name
├─ Session type
├─ Gross amount
├─ Fees (20%)
├─ Net earned
└─ Status
```

**Tasks**:
```
BACKEND (1 hour):
- [ ] Create payment history endpoint
- [ ] Create invoice generation
- [ ] Email invoice to student
- [ ] PDF invoice generation

FRONTEND (1 hour):
- [ ] Create payment history page
- [ ] Display in dashboard
- [ ] Download receipt button
- [ ] Email receipt button
```

---

## 📌 GUIDE 2: QUIZ SYSTEM (12 hours)

### Overview
Interactive quiz system with multiple question types

### Feature 1: Quiz Creation (3 hours)

**Mentor Can Create**:
```
Quiz Details
├─ Title
├─ Description
├─ Duration
├─ Passing score
├─ Retake policy
└─ Assignment to courses

Questions (Multiple types)
├─ Multiple choice (4 options)
├─ True/False
├─ Short answer (auto-graded by keyword)
├─ Essay (manual grading)
└─ Code challenge (optional)

Question Editor
├─ Rich text editor for questions
├─ Add images
├─ Shuffle options (optional)
└─ Mark answer as correct
```

**Endpoints**:
```
POST /api/v1x/quizzes
PATCH /api/v1x/quizzes/{id}
POST /api/v1x/quizzes/{id}/questions
DELETE /api/v1x/quizzes/{id}/questions/{question_id}
```

**Tasks**:
```
BACKEND (1.5 hours):
- [ ] Create Quiz model
- [ ] Create Question model
- [ ] Create answer options model
- [ ] Add validation
- [ ] Add permission checks

FRONTEND (1.5 hours):
- [ ] Create quiz builder page
- [ ] Question editor
- [ ] Add/remove questions
- [ ] Question type selector
- [ ] Drag-drop reordering
```

### Feature 2: Quiz Taking (4 hours)

**Student Experience**:
```
1. See quiz info
   ├─ Duration
   ├─ Questions count
   ├─ Passing score
   └─ Start button

2. Take quiz
   ├─ Timer (show time remaining)
   ├─ Progress bar
   ├─ Question navigation
   ├─ Submit answer
   └─ Next/Previous buttons

3. Review (optional)
   ├─ Show all answers
   ├─ Show correct answers
   ├─ Show explanations
   └─ Retake button (if allowed)
```

**Endpoints**:
```
POST /api/v1x/quizzes/{id}/start
POST /api/v1x/quizzes/{id}/submit-answer
POST /api/v1x/quizzes/{id}/finish
GET /api/v1x/quizzes/{id}/responses/{response_id}
```

**Tasks**:
```
BACKEND (2 hours):
- [ ] Create quiz response model
- [ ] Auto-grade multiple choice
- [ ] Grade true/false
- [ ] Grade short answer (keyword matching)
- [ ] Calculate score
- [ ] Add time validation

FRONTEND (2 hours):
- [ ] Create quiz page
- [ ] Display questions
- [ ] Timer countdown
- [ ] Show progress
- [ ] Submit answers
- [ ] Show score
- [ ] Show results/explanations
```

### Feature 3: Grading & Results (3 hours)

**Student Results**:
```
Score Card
├─ Overall score
├─ Passing/failing
├─ Score breakdown per section
├─ Time spent
├─ Correct/incorrect count

Detailed Results
├─ Each question with answer
├─ Correct answer shown
├─ Explanation
├─ Mentor notes (if added)
└─ Reattempt option
```

**Mentor Grading**:
```
For essays/short answers:
├─ List of submissions
├─ View student answer
├─ Grade (points)
├─ Feedback text
├─ Save grades
└─ Email feedback to student
```

**Endpoints**:
```
GET /api/v1x/quizzes/{id}/responses
PATCH /api/v1x/quizzes/{id}/responses/{response_id}
POST /api/v1x/quizzes/{id}/responses/{response_id}/grade
```

**Tasks**:
```
BACKEND (1.5 hours):
- [ ] Calculate scores
- [ ] Determine pass/fail
- [ ] Store essay grades
- [ ] Generate certificates (if passed)
- [ ] Email results to student

FRONTEND (1.5 hours):
- [ ] Results page
- [ ] Score display
- [ ] Review answers
- [ ] Mentor grading interface
- [ ] Show feedback
```

### Feature 4: Analytics & Reporting (2 hours)

**Mentor Dashboard**:
```
Quiz Analytics
├─ Quiz list with stats
├─ Average score
├─ Pass rate
├─ Time analysis
├─ Most missed questions
└─ Student performance chart

Question Analytics
├─ Which questions students struggle with
├─ Average score per question
├─ Discrimination index
└─ Difficulty analysis
```

**Tasks**:
```
BACKEND (1 hour):
- [ ] Calculate quiz statistics
- [ ] Calculate question statistics
- [ ] Track attempt history
- [ ] Generate analytics data

FRONTEND (1 hour):
- [ ] Create analytics dashboard
- [ ] Show charts (bar, line, pie)
- [ ] Export analytics as CSV
- [ ] Performance over time
```

---

## 🗂️ FILE STRUCTURE FOR PHASE 3

```
PAYMENT SYSTEM:
src/pages/
├─ booking.tsx (ENHANCE: Add payment)
└─ payments/
   ├─ history.tsx (New)
   └─ receipts.tsx (New)

src/components/
├─ PaymentForm.tsx (New)
├─ StripeCardElement.tsx (New)
└─ PayoutCard.tsx (New)

QUIZ SYSTEM:
src/pages/
└─ courses/[id]/quizzes/
   ├─ index.tsx (List quizzes)
   ├─ [quizId]/
   │  ├─ take.tsx (Take quiz)
   │  ├─ results.tsx (View results)
   │  ├─ grade.tsx (Mentor grading)
   │  └─ edit.tsx (Edit quiz)
   └─ create.tsx (Create quiz)

src/components/
├─ QuizBuilder.tsx (New)
├─ QuestionEditor.tsx (New)
├─ QuizTaker.tsx (New)
├─ QuizResults.tsx (New)
└─ GradingPanel.tsx (New)
```

---

## 💻 QUICK CODE EXAMPLES

### Payment Form Component
```tsx
// src/components/PaymentForm.tsx
import { CardElement, useStripe } from '@stripe/react-stripe-js'

export default function PaymentForm({ amount, onSuccess }) {
  const stripe = useStripe()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // Create payment intent
      const res = await fetch('/api/v1x/payments/intent', {
        method: 'POST',
        body: JSON.stringify({ amount })
      })
      const { clientSecret } = await res.json()
      
      // Confirm payment
      const result = await stripe.confirmCardPayment(clientSecret)
      
      if (result.paymentIntent.status === 'succeeded') {
        onSuccess(result.paymentIntent.id)
      }
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <CardElement />
      {error && <div className="text-red-500">{error}</div>}
      <button 
        type="submit" 
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded"
      >
        {loading ? 'Processing...' : `Pay $${amount}`}
      </button>
    </form>
  )
}
```

### Quiz Taker Component
```tsx
// src/components/QuizTaker.tsx
export default function QuizTaker({ quiz }) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [timeLeft, setTimeLeft] = useState(quiz.duration * 60)
  
  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => prev - 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const handleAnswer = (answer) => {
    setAnswers({
      ...answers,
      [quiz.questions[currentQuestion].id]: answer
    })
  }

  const handleSubmit = async () => {
    // Send answers to backend
    await fetch(`/api/v1x/quizzes/${quiz.id}/finish`, {
      method: 'POST',
      body: JSON.stringify(answers)
    })
  }

  const question = quiz.questions[currentQuestion]
  
  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex justify-between mb-4">
        <span>Question {currentQuestion + 1} of {quiz.questions.length}</span>
        <span className="text-red-600">{Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}</span>
      </div>
      
      <h2 className="text-xl font-bold mb-6">{question.text}</h2>
      
      {question.type === 'multiple_choice' && (
        <div className="space-y-3">
          {question.options.map((opt, i) => (
            <label key={i} className="flex items-center p-3 border rounded cursor-pointer hover:bg-gray-100">
              <input 
                type="radio" 
                name="answer"
                checked={answers[question.id] === opt.id}
                onChange={() => handleAnswer(opt.id)}
              />
              <span className="ml-3">{opt.text}</span>
            </label>
          ))}
        </div>
      )}
      
      <div className="flex gap-4 mt-8">
        <button 
          onClick={() => setCurrentQuestion(prev => prev - 1)}
          disabled={currentQuestion === 0}
          className="px-4 py-2 border rounded"
        >
          Previous
        </button>
        <button 
          onClick={() => setCurrentQuestion(prev => prev + 1)}
          disabled={currentQuestion === quiz.questions.length - 1}
          className="px-4 py-2 border rounded"
        >
          Next
        </button>
        {currentQuestion === quiz.questions.length - 1 && (
          <button 
            onClick={handleSubmit}
            className="px-4 py-2 bg-green-600 text-white rounded"
          >
            Submit Quiz
          </button>
        )}
      </div>
    </div>
  )
}
```

---

## 🧪 TESTING CHECKLIST

### Payment System
- [ ] Stripe keys loaded correctly
- [ ] Payment form renders
- [ ] Test card accepted (4242 4242 4242 4242)
- [ ] Test card declined works
- [ ] Payment intent created
- [ ] Booking created after payment
- [ ] Payment recorded in database
- [ ] Email confirmation sent
- [ ] Payout calculated correctly
- [ ] Webhook received correctly

### Quiz System
- [ ] Quiz created successfully
- [ ] Questions added/removed
- [ ] Quiz displayed correctly
- [ ] Timer works
- [ ] Answers saved
- [ ] Score calculated
- [ ] Multiple choice graded
- [ ] Short answer keywords matched
- [ ] Essay shows for grading
- [ ] Certificate generated (if applicable)
- [ ] Analytics calculated

---

## ⏱️ TIME BREAKDOWN

| Component | Hours | Status |
|-----------|-------|--------|
| Stripe Setup | 3 | ⏳ |
| Booking Payment | 4 | ⏳ |
| Payout System | 3 | ⏳ |
| Invoices | 2 | ⏳ |
| Quiz Creation | 3 | ⏳ |
| Quiz Taking | 4 | ⏳ |
| Grading | 3 | ⏳ |
| Analytics | 2 | ⏳ |
| **TOTAL** | **24** | |

---

## 🚀 QUICK START

### Payment (12 hours total)
```
Day 1: Stripe setup + intent endpoint (3h)
Day 2: Payment form + booking integration (4h)
Day 3: Payout system (3h)
Day 4: Invoices + testing (2h)
```

### Quiz (12 hours total)
```
Day 5: Quiz creation UI (3h)
Day 6: Quiz taking + timer (4h)
Day 7: Grading system (3h)
Day 8: Analytics (2h)
```

---

## 📚 DEPENDENCIES

### Libraries to Install
```bash
npm install @stripe/react-stripe-js @stripe/js
npm install date-fns (for timing)
npm install recharts (for analytics charts)
npm install html2pdf (for PDF generation)
```

### Python Libraries
```bash
pip install stripe
pip install python-dotenv
```

---

## 💳 STRIPE TEST CARDS

For testing in Stripe test mode:

**Successful Payment**:
- Card: 4242 4242 4242 4242
- Expiry: Any future date
- CVC: Any 3 digits

**Declined Card**:
- Card: 4000 0000 0000 0002
- Expiry: Any future date
- CVC: Any 3 digits

---

**Phase**: 3 of 4  
**Total Hours**: 24 (12 payment + 12 quiz)  
**Start**: Week 2-3  
**Dependencies**: Week 1 (Dashboard testing + mentor features)

✅ **READY TO IMPLEMENT!**
