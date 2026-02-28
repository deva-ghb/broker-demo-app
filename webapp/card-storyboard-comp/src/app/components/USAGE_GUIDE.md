# InfoCard Component - Complete Usage Guide

## Quick Start

### 1. Import the Components
```typescript
import { InfoCard, CardData } from './components/InfoCard';
import { 
  createTableCard, 
  createSimpleCard, 
  createNestedCard 
} from './utils/cardHelpers';
```

### 2. Create Your Card Data

#### Option A: Manual Creation
```typescript
const myCard: CardData = {
  id: 'unique-id',
  title: 'Card Title',
  subtitle: 'Optional Subtitle',
  contentType: 'text',
  textContent: {
    main: 'Large\nText',
    supporting: 'Supporting description'
  },
  detailType: 'table',
  tableDetails: [
    { label: 'Label', value: 'Value' },
    // ... more details
  ]
};
```

#### Option B: Using Helper Functions
```typescript
const myCard = createTableCard(
  'unique-id',
  'Card Title',
  [
    { label: 'Label', value: 'Value' },
  ],
  {
    subtitle: 'Optional Subtitle',
    contentType: 'text',
    textContent: { supporting: 'Description' }
  }
);
```

### 3. Render the Card
```typescript
const [expandedId, setExpandedId] = useState<string | null>(null);

<InfoCard
  card={myCard}
  isExpanded={expandedId === myCard.id}
  onToggle={() => setExpandedId(expandedId === myCard.id ? null : myCard.id)}
/>
```

---

## Card Types Reference

### Type 1: Table Details Card
**Best for:** Structured data, specifications, pricing breakdowns

```typescript
const card = createTableCard(
  'card-1',
  'Property Specifications',
  [
    { label: 'Type', value: '2 BHK' },
    { label: 'Size', value: '1,200 sqft' },
    { label: 'Price', value: 'AED 1.8M' },
  ]
);
```

**Details Display:** Two-column key-value layout

---

### Type 2: Simple Text Card
**Best for:** Descriptions, explanations, policies

```typescript
const card = createSimpleCard(
  'card-2',
  'Investment Strategy',
  'This is a longer description that explains the concept in detail. Maximum recommended length is 3-4 lines for optimal readability.'
);
```

**Details Display:** Paragraph text, max 3-4 lines

---

### Type 3: Nested Cards
**Best for:** Amenities, galleries, feature showcases

```typescript
const card = createNestedCard(
  'card-3',
  'Amenities',
  [
    {
      image: 'https://...',
      title: 'Swimming Pool',
      description: 'Olympic-sized pool with separate kids area.',
      details: [
        { label: 'Access', value: 'Residents only' },
        { label: 'Hours', value: '6 AM - 10 PM' },
      ]
    },
    // 5-7 nested cards recommended
  ]
);
```

**Details Display:** Image carousel with navigation and dots

---

## Content Types

### Text Content
```typescript
{
  contentType: 'text',
  textContent: {
    main: 'AED\n600,000+',  // Large highlighted text
    supporting: 'Description'  // Smaller supporting text
  }
}
```

### Image Content
```typescript
{
  contentType: 'image',
  imageContent: 'https://...' // or imported image
}
```

### Video Content
```typescript
{
  contentType: 'video',
  videoContent: 'https://...' // Video URL
}
```

---

## Complete Examples

### Example 1: Financial Card with Large Number
```typescript
const financialCard = createTableCard(
  'cost-of-waiting',
  'The Cost of Waiting',
  [
    { label: 'Annual rent', value: 'AED 120,000' },
    { label: '5-year total', value: 'AED 600,000+' },
    { label: 'Equity built', value: 'AED 0' },
  ],
  {
    contentType: 'text',
    textContent: {
      main: 'AED\n600,000+',
      supporting: 'Total rental expenditure over five years creates zero wealth.'
    }
  }
);
```

### Example 2: Property Listing with Image
```typescript
const propertyCard = createTableCard(
  'property-1',
  'Treppan Living Privé',
  [
    { label: 'Type', value: '2 BHK + Study' },
    { label: 'Size', value: '1,250 - 1,480 sqft' },
    { label: 'Price', value: 'AED 2.1M - 2.4M' },
  ],
  {
    subtitle: 'Q3 2026 Handover',
    contentType: 'image',
    imageContent: propertyImage
  }
);
```

### Example 3: Amenities Carousel
```typescript
const amenitiesCard = createNestedCard(
  'amenities',
  'Premium Amenities',
  [
    createNestedCardItem(
      poolImage,
      'Infinity Pool',
      'Temperature-controlled pool with city views.',
      [
        { label: 'Access', value: 'Residents only' },
        { label: 'Safety', value: 'Lifeguard on duty' }
      ]
    ),
    createNestedCardItem(
      gymImage,
      'Fitness Center',
      '24/7 access to state-of-the-art equipment.',
      [
        { label: 'Hours', value: '24/7' },
        { label: 'Trainers', value: 'Available' }
      ]
    ),
    // Add 3-5 more amenities
  ],
  {
    subtitle: 'World-class facilities',
    contentType: 'text',
    textContent: {
      supporting: 'Exclusive facilities for residents'
    }
  }
);
```

---

## Full App Implementation

```typescript
import { useState } from 'react';
import { InfoCard, CardData } from './components/InfoCard';

export default function App() {
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);
  
  const cards: CardData[] = [
    // Your cards here
  ];

  return (
    <div className="bg-black h-screen overflow-hidden">
      {/* Cards container */}
      <div className="flex gap-4 px-8 overflow-x-auto scrollbar-hide">
        {cards.map((card) => (
          <InfoCard
            key={card.id}
            card={card}
            isExpanded={expandedCardId === card.id}
            onToggle={() => setExpandedCardId(
              expandedCardId === card.id ? null : card.id
            )}
          />
        ))}
      </div>
      
      {/* Carousel indicators */}
      <div className="flex justify-center gap-2 mt-6">
        {cards.map((card) => (
          <div
            key={card.id}
            className={`h-1 rounded-full transition-all ${
              expandedCardId === card.id ? 'w-10 bg-white' : 'w-6 bg-white/30'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
```

---

## Best Practices

### Card Content Guidelines
- **Title:** Keep under 30 characters
- **Subtitle:** Optional, use for dates or categories
- **Table Details:** 3-5 items optimal, max 7
- **Simple Details:** 2-4 lines of text
- **Nested Cards:** 5-7 items optimal for carousel

### Performance Tips
- Use imported images from Figma assets when available
- Lazy load videos for better performance
- Limit nested cards to 7 items maximum

### Accessibility
- All cards are keyboard accessible (tappable/clickable)
- Carousel navigation with arrow buttons
- Visual indicators for expanded state

### Styling Consistency
- All cards use glassmorphism design
- Consistent 32px border radius
- White/12% border opacity
- Instrument Sans for headings, Inter for body text

---

## Troubleshooting

### Cards not expanding?
- Ensure you're managing the `expandedCardId` state
- Check that `onToggle` is properly connected

### Images not loading?
- Use `figma:asset/...` for Figma imports (no path prefix!)
- Use full URLs for external images
- Check image paths are correct

### Nested cards navigation not working?
- Navigation buttons are built-in, ensure images are loading
- Click events are stopped from propagating to parent

### Styling issues?
- Import fonts in `/src/styles/fonts.css`
- Add scrollbar-hide utility to `/src/styles/index.css`
- Check Tailwind is properly configured
