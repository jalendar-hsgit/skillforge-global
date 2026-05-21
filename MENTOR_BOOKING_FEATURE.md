# MENTOR BOOKING FEATURE - COMPLETE GUIDE

## 🎯 Overview

Students can now browse mentors, check their availability, and book sessions.

---

## 📋 MENTOR URLS FOR STUDENTS/BUYERS

### Browse & Filter Mentors

```
GET /mentors
  Description: List all mentors with filters
  Query Params:
    ?expertise=python          - Filter by expertise
    ?expertise=python-ai       - Can be multiple separated by comma
    ?rate_min=50               - Minimum hourly rate
    ?rate_max=100              - Maximum hourly rate
    ?rating_min=4              - Minimum rating
    ?page=1                    - Pagination
    ?limit=10                  - Results per page
  
  Response:
  {
    "mentors": [
      {
        "id": 1,
        "name": "Sarah Chen",
        "bio": "Expert in Python and AI",
        "expertise": ["python-ai", "ml"],
        "hourly_rate": 75,
        "average_rating": 4.8,
        "total_students": 42,
        "image_url": "..."
      }
    ],
    "total": 4,
    "page": 1,
    "limit": 10
  }
```

### View Mentor Profile

```
GET /mentors/[mentorId]
  Response:
  {
    "id": 1,
    "name": "Sarah Chen",
    "bio": "10+ years Python & AI experience",
    "expertise": ["python-ai", "ml", "deep-learning"],
    "hourly_rate": 75,
    "average_rating": 4.8,
    "total_students": 42,
    "reviews_count": 15,
    "response_time": "< 2 hours",
    "image_url": "...",
    "certifications": ["AWS", "Google Cloud"],
    "teaching_style": "Interactive & hands-on",
    "availability_status": "Available"
  }
```

### Check Mentor Availability

```
GET /mentors/[mentorId]/availability
  Response:
  {
    "mentor_id": 1,
    "mentor_name": "Sarah Chen",
    "available_slots": [
      {
        "date": "2026-02-03",
        "day": "Monday",
        "slots": [
          { "time": "09:00", "available": true, "price": 75 },
          { "time": "10:00", "available": true, "price": 75 },
          { "time": "11:00", "available": false, "booked": true },
          { "time": "14:00", "available": true, "price": 75 },
          { "time": "15:00", "available": true, "price": 75 }
        ]
      },
      {
        "date": "2026-02-04",
        "day": "Tuesday",
        "slots": [
          { "time": "09:00", "available": true, "price": 75 },
          // ... more slots
        ]
      }
    ]
  }
```

### View Mentor Reviews

```
GET /mentors/[mentorId]/reviews
  Response:
  {
    "mentor_id": 1,
    "mentor_name": "Sarah Chen",
    "average_rating": 4.8,
    "total_reviews": 15,
    "reviews": [
      {
        "id": 1,
        "student_name": "John Doe",
        "rating": 5,
        "comment": "Great mentor! Very knowledgeable",
        "date": "2026-01-25",
        "verified": true
      },
      {
        "id": 2,
        "student_name": "Jane Smith",
        "rating": 5,
        "comment": "Excellent teaching style",
        "date": "2026-01-20",
        "verified": true
      }
    ]
  }
```

### Book a Session

```
POST /mentors/[mentorId]/book
  Headers: Authorization: Bearer <token>
  Body:
  {
    "date": "2026-02-03",
    "time": "09:00",
    "topic": "Python Web Development",
    "duration_minutes": 60,
    "notes": "I'm new to Django, need help with basics"
  }

  Response:
  {
    "session_id": 5,
    "mentor_id": 1,
    "mentor_name": "Sarah Chen",
    "student_name": "John Doe",
    "scheduled_at": "2026-02-03T09:00:00Z",
    "duration_minutes": 60,
    "price": 75,
    "status": "PENDING_CONFIRMATION",
    "meeting_url": "https://meet.example.com/abc123",
    "next_step": "Wait for mentor confirmation"
  }
```

### List My Booked Sessions

```
GET /dashboard/mentor-sessions
  Headers: Authorization: Bearer <token>
  Response:
  {
    "sessions": [
      {
        "id": 5,
        "mentor_id": 1,
        "mentor_name": "Sarah Chen",
        "scheduled_at": "2026-02-03T09:00:00Z",
        "duration_minutes": 60,
        "topic": "Python Web Development",
        "status": "PENDING_CONFIRMATION",
        "price": 75,
        "meeting_url": "https://meet.example.com/abc123"
      },
      {
        "id": 4,
        "mentor_name": "David Kumar",
        "scheduled_at": "2026-01-30T14:00:00Z",
        "status": "COMPLETED",
        "price": 65
      }
    ]
  }
```

### Leave Session Feedback

```
POST /dashboard/mentor-sessions/[sessionId]/feedback
  Headers: Authorization: Bearer <token>
  Body:
  {
    "rating": 5,
    "comment": "Great session! Learned a lot about Django.",
    "would_recommend": true
  }

  Response:
  {
    "session_id": 5,
    "feedback_submitted": true,
    "message": "Thank you for your feedback!"
  }
```

---

## 📱 FRONTEND COMPONENTS

### 1. Browse Mentors Page

**File: src/pages/mentors/index.tsx**
```typescript
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function MentorsPage() {
  const [mentors, setMentors] = useState([]);
  const [filters, setFilters] = useState({
    expertise: '',
    rate_min: 0,
    rate_max: 200,
    rating_min: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMentors();
  }, [filters]);

  const fetchMentors = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.expertise) params.append('expertise', filters.expertise);
      if (filters.rate_min) params.append('rate_min', filters.rate_min);
      if (filters.rate_max) params.append('rate_max', filters.rate_max);
      if (filters.rating_min) params.append('rating_min', filters.rating_min);

      const response = await fetch(`/api/v1x/mentors?${params}`);
      const data = await response.json();
      setMentors(data.mentors || []);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading mentors...</div>;

  return (
    <div className="mentors-page">
      <header className="page-header">
        <h1>Find a Mentor</h1>
        <p>Connect with experts and accelerate your learning</p>
      </header>

      {/* Filters Sidebar */}
      <div className="page-layout">
        <aside className="filters-sidebar">
          <h3>Filter Mentors</h3>
          
          <div className="filter-group">
            <label>Expertise</label>
            <select 
              value={filters.expertise}
              onChange={(e) => setFilters({...filters, expertise: e.target.value})}
            >
              <option value="">All Expertise</option>
              <option value="python-ai">Python & AI</option>
              <option value="web-dev">Web Development</option>
              <option value="ml">Machine Learning</option>
              <option value="devops">DevOps</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Hourly Rate</label>
            <input 
              type="range" 
              min="0" 
              max="200"
              value={filters.rate_max}
              onChange={(e) => setFilters({...filters, rate_max: parseInt(e.target.value)})}
            />
            <p>${filters.rate_min} - ${filters.rate_max}/hr</p>
          </div>

          <div className="filter-group">
            <label>Minimum Rating</label>
            <select
              value={filters.rating_min}
              onChange={(e) => setFilters({...filters, rating_min: parseInt(e.target.value)})}
            >
              <option value={0}>Any Rating</option>
              <option value={4}>4+ Stars</option>
              <option value={4.5}>4.5+ Stars</option>
              <option value={5}>5 Stars</option>
            </select>
          </div>
        </aside>

        {/* Mentors Grid */}
        <main className="mentors-grid">
          {mentors.length === 0 ? (
            <div className="no-results">
              <p>No mentors found. Try adjusting your filters.</p>
            </div>
          ) : (
            mentors.map(mentor => (
              <div key={mentor.id} className="mentor-card">
                <div className="mentor-header">
                  <img src={mentor.image_url} alt={mentor.name} />
                  <div className="mentor-info">
                    <h3>{mentor.name}</h3>
                    <p className="expertise">
                      {mentor.expertise.join(', ')}
                    </p>
                  </div>
                </div>

                <p className="bio">{mentor.bio}</p>

                <div className="mentor-stats">
                  <div className="stat">
                    <span className="label">Rate</span>
                    <span className="value">${mentor.hourly_rate}/hr</span>
                  </div>
                  <div className="stat">
                    <span className="label">Rating</span>
                    <span className="value">★ {mentor.average_rating}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Students</span>
                    <span className="value">{mentor.total_students}</span>
                  </div>
                </div>

                <div className="mentor-actions">
                  <Link href={`/mentors/${mentor.id}`}>
                    <a className="btn btn-secondary">View Profile</a>
                  </Link>
                  <Link href={`/mentors/${mentor.id}/book`}>
                    <a className="btn btn-primary">Book Now</a>
                  </Link>
                </div>
              </div>
            ))
          )}
        </main>
      </div>
    </div>
  );
}
```

### 2. Mentor Profile Page

**File: src/pages/mentors/[id].tsx**
```typescript
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function MentorProfile() {
  const router = useRouter();
  const { id } = router.query;
  const [mentor, setMentor] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    
    Promise.all([
      fetch(`/api/v1x/mentors/${id}`).then(r => r.json()),
      fetch(`/api/v1x/mentors/${id}/reviews`).then(r => r.json())
    ]).then(([mentorData, reviewsData]) => {
      setMentor(mentorData);
      setReviews(reviewsData.reviews || []);
    }).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Loading profile...</div>;
  if (!mentor) return <div>Mentor not found</div>;

  return (
    <div className="mentor-profile">
      {/* Header Section */}
      <div className="profile-header">
        <div className="mentor-image">
          <img src={mentor.image_url} alt={mentor.name} />
        </div>
        
        <div className="mentor-details">
          <h1>{mentor.name}</h1>
          
          <div className="rating">
            <span className="stars">
              {'★'.repeat(Math.round(mentor.average_rating))}
              {'☆'.repeat(5 - Math.round(mentor.average_rating))}
            </span>
            <span className="rating-value">{mentor.average_rating}/5</span>
            <span className="reviews-count">({mentor.reviews_count} reviews)</span>
          </div>

          <p className="bio">{mentor.bio}</p>

          <div className="quick-stats">
            <div className="stat">
              <span className="label">Hourly Rate</span>
              <span className="value">${mentor.hourly_rate}</span>
            </div>
            <div className="stat">
              <span className="label">Students</span>
              <span className="value">{mentor.total_students}</span>
            </div>
            <div className="stat">
              <span className="label">Response Time</span>
              <span className="value">{mentor.response_time}</span>
            </div>
            <div className="stat">
              <span className="label">Status</span>
              <span className="value badge badge-success">
                {mentor.availability_status}
              </span>
            </div>
          </div>

          <Link href={`/mentors/${mentor.id}/book`}>
            <a className="btn btn-primary btn-large">Book a Session</a>
          </Link>
        </div>
      </div>

      {/* About Section */}
      <section className="profile-section">
        <h2>About</h2>
        <p>{mentor.bio}</p>

        <h3>Expertise</h3>
        <div className="expertise-tags">
          {mentor.expertise.map(exp => (
            <span key={exp} className="tag">{exp}</span>
          ))}
        </div>

        {mentor.certifications && (
          <>
            <h3>Certifications</h3>
            <ul className="certifications-list">
              {mentor.certifications.map(cert => (
                <li key={cert}>✓ {cert}</li>
              ))}
            </ul>
          </>
        )}

        <h3>Teaching Style</h3>
        <p>{mentor.teaching_style}</p>
      </section>

      {/* Reviews Section */}
      <section className="profile-section">
        <h2>Student Reviews ({mentor.reviews_count})</h2>
        
        {reviews.length === 0 ? (
          <p>No reviews yet</p>
        ) : (
          <div className="reviews-list">
            {reviews.map(review => (
              <div key={review.id} className="review-item">
                <div className="review-header">
                  <div className="reviewer-info">
                    <h4>{review.student_name}</h4>
                    {review.verified && (
                      <span className="badge badge-success">Verified</span>
                    )}
                  </div>
                  <div className="review-rating">
                    {'★'.repeat(review.rating)}
                    {'☆'.repeat(5 - review.rating)}
                  </div>
                </div>
                <p className="review-comment">{review.comment}</p>
                <span className="review-date">
                  {new Date(review.date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Availability Section */}
      <section className="profile-section">
        <h2>Availability</h2>
        <Link href={`/mentors/${mentor.id}/availability`}>
          <a className="btn btn-secondary">View Full Calendar</a>
        </Link>
      </section>
    </div>
  );
}
```

### 3. Book Session Page

**File: src/pages/mentors/[id]/book.tsx**
```typescript
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

export default function BookSessionPage() {
  const router = useRouter();
  const { id } = router.query;
  const [mentor, setMentor] = useState(null);
  const [availability, setAvailability] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [topic, setTopic] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    
    Promise.all([
      fetch(`/api/v1x/mentors/${id}`).then(r => r.json()),
      fetch(`/api/v1x/mentors/${id}/availability`).then(r => r.json())
    ]).then(([mentorData, availData]) => {
      setMentor(mentorData);
      setAvailability(availData.available_slots || []);
      if (availData.available_slots && availData.available_slots[0]) {
        setSelectedDate(availData.available_slots[0].date);
      }
    }).finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1x/mentors/${id}/book`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          date: selectedDate,
          time: selectedTime,
          topic,
          duration_minutes: 60,
          notes
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert('Session booked! Waiting for mentor confirmation.');
        router.push('/dashboard/mentor-sessions');
      } else {
        alert('Failed to book session');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!mentor) return <div>Mentor not found</div>;

  const currentSlots = availability.find(a => a.date === selectedDate)?.slots || [];

  return (
    <div className="book-session-page">
      <header className="page-header">
        <h1>Book a Session with {mentor.name}</h1>
        <p>Rate: ${mentor.hourly_rate}/hour</p>
      </header>

      <form onSubmit={handleSubmit} className="booking-form">
        <section>
          <h2>Select Date & Time</h2>
          
          <div className="form-group">
            <label>Date</label>
            <select 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              required
            >
              <option value="">Choose a date...</option>
              {availability.map(slot => (
                <option key={slot.date} value={slot.date}>
                  {slot.day}, {new Date(slot.date).toLocaleDateString()}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Time</label>
            <div className="time-slots">
              {currentSlots.length === 0 ? (
                <p>No available times for this date</p>
              ) : (
                currentSlots.map(slot => (
                  <button
                    key={slot.time}
                    type="button"
                    className={`time-slot ${!slot.available ? 'disabled' : ''} ${
                      selectedTime === slot.time ? 'selected' : ''
                    }`}
                    disabled={!slot.available}
                    onClick={() => setSelectedTime(slot.time)}
                  >
                    {slot.time}
                  </button>
                ))
              )}
            </div>
          </div>
        </section>

        <section>
          <h2>Session Details</h2>
          
          <div className="form-group">
            <label>Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Django Basics, REST API Design"
              required
            />
          </div>

          <div className="form-group">
            <label>Duration</label>
            <select>
              <option>60 minutes</option>
              <option>90 minutes</option>
              <option>120 minutes</option>
            </select>
          </div>

          <div className="form-group">
            <label>Additional Notes (optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Tell the mentor about your goals, experience level, or any specific questions..."
              rows={4}
            />
          </div>
        </section>

        <section className="summary">
          <h2>Booking Summary</h2>
          <div className="summary-item">
            <span>Mentor</span>
            <strong>{mentor.name}</strong>
          </div>
          <div className="summary-item">
            <span>Date & Time</span>
            <strong>{selectedDate} at {selectedTime}</strong>
          </div>
          <div className="summary-item">
            <span>Duration</span>
            <strong>60 minutes</strong>
          </div>
          <div className="summary-item">
            <span>Price</span>
            <strong>${mentor.hourly_rate}</strong>
          </div>
        </section>

        <button 
          type="submit" 
          className="btn btn-primary btn-large"
          disabled={!selectedDate || !selectedTime || !topic || submitting}
        >
          {submitting ? 'Booking...' : 'Confirm Booking'}
        </button>
      </form>
    </div>
  );
}
```

### 4. My Sessions Page

**File: src/pages/dashboard/mentor-sessions.tsx**
```typescript
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function MySessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, pending, confirmed, completed

  useEffect(() => {
    fetchSessions();
  }, [filter]);

  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = filter === 'all' 
        ? '/api/v1x/dashboard/mentor-sessions'
        : `/api/v1x/dashboard/mentor-sessions?status=${filter}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setSessions(data.sessions || []);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="mentor-sessions-page">
      <header>
        <h1>My Mentor Sessions</h1>
      </header>

      <div className="filter-tabs">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All Sessions
        </button>
        <button 
          className={filter === 'pending' ? 'active' : ''}
          onClick={() => setFilter('pending')}
        >
          Pending Confirmation
        </button>
        <button 
          className={filter === 'confirmed' ? 'active' : ''}
          onClick={() => setFilter('confirmed')}
        >
          Confirmed
        </button>
        <button 
          className={filter === 'completed' ? 'active' : ''}
          onClick={() => setFilter('completed')}
        >
          Completed
        </button>
      </div>

      {sessions.length === 0 ? (
        <div className="no-sessions">
          <p>No sessions found</p>
          <Link href="/mentors">
            <a className="btn btn-primary">Find a Mentor</a>
          </Link>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map(session => (
            <div key={session.id} className="session-card">
              <div className="session-header">
                <h3>{session.mentor_name}</h3>
                <span className={`badge badge-${session.status.toLowerCase()}`}>
                  {session.status}
                </span>
              </div>

              <div className="session-details">
                <p><strong>Topic:</strong> {session.topic}</p>
                <p><strong>Date & Time:</strong> {new Date(session.scheduled_at).toLocaleString()}</p>
                <p><strong>Duration:</strong> {session.duration_minutes} minutes</p>
                <p><strong>Price:</strong> ${session.price}</p>
              </div>

              <div className="session-actions">
                {session.status === 'CONFIRMED' && (
                  <a href={session.meeting_url} className="btn btn-primary" target="_blank">
                    Join Meeting
                  </a>
                )}
                {session.status === 'COMPLETED' && (
                  <Link href={`/dashboard/mentor-sessions/${session.id}/feedback`}>
                    <a className="btn btn-secondary">Leave Feedback</a>
                  </Link>
                )}
                {session.status === 'PENDING_CONFIRMATION' && (
                  <span className="waiting-text">Waiting for mentor confirmation...</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 DEMO DATA FOR MENTORS

```sql
-- Mentors in Database (4 total)
1. Sarah Chen
   - Expertise: python-ai, ml, deep-learning
   - Rate: $75/hour
   - Rating: 4.8/5
   - Students: 42
   - Reviews: 15

2. David Kumar
   - Expertise: web-dev, javascript, react
   - Rate: $65/hour
   - Rating: 4.7/5
   - Students: 38
   - Reviews: 12

3. Emily Rodriguez
   - Expertise: ml, data-science, python-ai
   - Rate: $85/hour
   - Rating: 4.9/5
   - Students: 51
   - Reviews: 20

4. James Patterson
   - Expertise: devops, kubernetes, aws
   - Rate: $70/hour
   - Rating: 4.6/5
   - Students: 35
   - Reviews: 10

-- Mentor Sessions (8 total)
- All scheduled for 7+ days from now
- Status: PENDING (waiting for mentor confirmation)
- Mix of different times and durations
- All with demo students
```

---

## ✅ IMPLEMENTATION CHECKLIST

Frontend Components:
- [ ] `/mentors` - Browse mentors page (list with filters)
- [ ] `/mentors/[id]` - Mentor profile page (reviews, bio, stats)
- [ ] `/mentors/[id]/book` - Booking form (date/time selection)
- [ ] `/mentors/[id]/availability` - Full availability calendar
- [ ] `/mentors/[id]/reviews` - All reviews page
- [ ] `/dashboard/mentor-sessions` - My sessions list
- [ ] `/dashboard/mentor-sessions/[id]/feedback` - Feedback form

Backend API Endpoints:
- [ ] `GET /api/v1x/mentors` - List mentors with filters
- [ ] `GET /api/v1x/mentors/[id]` - Get mentor profile
- [ ] `GET /api/v1x/mentors/[id]/availability` - Get available slots
- [ ] `GET /api/v1x/mentors/[id]/reviews` - Get mentor reviews
- [ ] `POST /api/v1x/mentors/[id]/book` - Book session
- [ ] `GET /api/v1x/dashboard/mentor-sessions` - Get my sessions
- [ ] `POST /api/v1x/dashboard/mentor-sessions/[id]/feedback` - Submit feedback

Styling:
- [ ] Mentor cards (image, name, expertise, rate, rating)
- [ ] Profile page layout
- [ ] Booking form with calendar
- [ ] Session cards
- [ ] Review cards
- [ ] Status badges (PENDING, CONFIRMED, COMPLETED)
- [ ] Responsive design

Testing:
- [ ] Can browse all 4 mentors
- [ ] Filters work (expertise, rate, rating)
- [ ] Can view mentor profile
- [ ] Can see mentor reviews
- [ ] Can check availability
- [ ] Can book a session
- [ ] Can view my sessions
- [ ] Can leave feedback
- [ ] All pages load demo data correctly

---

**Status**: Ready to implement ✅
