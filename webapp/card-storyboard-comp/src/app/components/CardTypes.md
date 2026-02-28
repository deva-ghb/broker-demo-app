# InfoCard Component - Three Card Types

## Overview
The InfoCard component supports three distinct card types with different detail views that appear when the card is tapped/clicked.

## Card Types

### 1. Card with Detail Table (Type: 'table')
**Purpose:** Display structured key-value pair information
**Use Case:** Property specifications, pricing breakdowns, feature comparisons

**Example Data:**
```typescript
{
  id: '1',
  title: 'Permanent Address Found',
  contentType: 'text',
  textContent: { supporting: '...' },
  detailType: 'table',
  tableDetails: [
    { label: 'Market Status', value: 'Dubai Residential' },
    { label: 'Tenure', value: '100% Freehold' },
    { label: 'Availability', value: 'Limited Private Units' }
  ]
}
```

**Features:**
- Clean two-column layout
- Left-aligned labels, right-aligned values
- Professional color scheme (gray labels, cream values)

---

### 2. Card with Simple Text (Type: 'simple')
**Purpose:** Display longer descriptive text
**Use Case:** Explanations, benefits descriptions, policy details

**Example Data:**
```typescript
{
  id: '3',
  title: 'Seamless Daily Transition',
  contentType: 'text',
  textContent: { supporting: '...' },
  detailType: 'simple',
  simpleDetails: 'Long form text that explains the concept in detail...'
}
```

**Features:**
- Maximum 3-4 lines of text
- Responsive text wrapping
- Optimal reading width

---

### 3. Card with Nested Cards (Type: 'nested')
**Purpose:** Showcase multiple sub-items with images
**Use Case:** Amenities showcase, feature galleries, property highlights

**Example Data:**
```typescript
{
  id: '5',
  title: 'Premium Amenities',
  contentType: 'text',
  detailType: 'nested',
  nestedCards: [
    {
      image: 'url-to-image.jpg',
      title: 'Family Wellness',
      description: 'A dedicated space for relaxation...',
      details: [
        { label: 'Access', value: 'Residents only' },
        { label: 'Safety', value: 'Lifeguard monitored' }
      ]
    },
    // ... 5-7 nested cards
  ]
}
```

**Features:**
- Image carousel with left/right navigation
- Each nested card shows:
  - Image (220px height)
  - 2-line personalized description
  - Optional detail table
- Carousel indicators (dots)
- Smooth transitions between items

---

## Main Content Types

The card's main content area can display three types:

### 1. Text Content (contentType: 'text')
- Large highlighted text (e.g., "AED 600,000+")
- Supporting description text
- Centered layout

### 2. Image Content (contentType: 'image')
- Full-width rounded image
- 314px height
- Object-fit cover

### 3. Video Content (contentType: 'video')
- Embedded video player
- Rounded corners
- Native controls

---

## Usage Example

```typescript
import { InfoCard, CardData } from './components/InfoCard';

const myCard: CardData = {
  id: 'unique-id',
  title: 'Card Title',
  subtitle: 'Optional subtitle',
  contentType: 'image',
  imageContent: 'https://...',
  detailType: 'nested',
  nestedCards: [...]
};

<InfoCard 
  card={myCard}
  isExpanded={expandedId === myCard.id}
  onToggle={() => handleToggle(myCard.id)}
/>
```

---

## Styling Notes

- All cards use glassmorphism effect
- Background gradient: -43.78deg
- Border: 0.587px white/12% opacity
- Fonts: Instrument Sans (headings), Inter (body)
- Rounded corners: 32px (card), 22px (images), 16px (nested details)
