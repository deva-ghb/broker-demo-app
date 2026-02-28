# InfoCard Component System - Complete Documentation

## 📦 What's Included

This project contains a complete, reusable card component system with three distinct card types, all matching the Figma design specifications.

### Files Created

```
/src/app/
├── components/
│   ├── InfoCard.tsx           # Main card component
│   ├── CardTypes.md           # Card types documentation
│   └── USAGE_GUIDE.md         # Complete usage guide
├── utils/
│   └── cardHelpers.ts         # Helper functions for creating cards
├── examples/
│   └── cardExamples.tsx       # Example implementations
└── App.tsx                    # Demo app with all card types

/src/styles/
├── fonts.css                  # Google Fonts imports
└── index.css                  # Custom scrollbar styles
```

---

## 🎴 Three Card Types

### 1. **Table Details Card**
- Displays structured key-value information
- Perfect for: Specifications, pricing, features
- Detail layout: Two-column table format

### 2. **Simple Text Card**
- Shows descriptive paragraph text
- Perfect for: Explanations, policies, descriptions
- Detail layout: Clean paragraph (max 3-4 lines)

### 3. **Nested Cards**
- Contains a carousel of sub-cards with images
- Perfect for: Amenities, galleries, feature showcases
- Detail layout: Image carousel with navigation arrows and dots
- Each nested card has: Image + Title + Description + Optional table

---

## 🎨 Card Content Types

Each card can display one of three content types in the main area:

1. **Text** - Large highlighted text with supporting description
2. **Image** - Full-width image with rounded corners
3. **Video** - Embedded video player

---

## ⚡ Quick Start

### Basic Usage

```typescript
import { InfoCard, CardData } from './components/InfoCard';
import { createTableCard } from './utils/cardHelpers';

// Create a card
const myCard = createTableCard(
  'card-1',
  'Property Details',
  [
    { label: 'Type', value: '2 BHK' },
    { label: 'Size', value: '1,200 sqft' },
    { label: 'Price', value: 'AED 1.8M' }
  ]
);

// Render it
<InfoCard 
  card={myCard}
  isExpanded={expandedId === myCard.id}
  onToggle={() => handleToggle(myCard.id)}
/>
```

### Using Helper Functions

```typescript
import { 
  createTableCard,      // For table details
  createSimpleCard,     // For text descriptions
  createNestedCard,     // For carousels
  createNestedCardItem, // For nested items
  CardTemplates         // Pre-built templates
} from './utils/cardHelpers';

// Use a template
const card = CardTemplates.propertyListing(
  'prop-1',
  'The Residences',
  imageUrl,
  'AED 3.2M',
  '2,100 sqft',
  '4 BHK Penthouse'
);
```

---

## 📋 Examples

### Example 1: Financial Card with Large Number
```typescript
const financialCard = createTableCard(
  'cost',
  'The Cost of Waiting',
  [
    { label: 'Annual rent', value: 'AED 120,000' },
    { label: '5-year total', value: 'AED 600,000+' },
  ],
  {
    contentType: 'text',
    textContent: {
      main: 'AED\n600,000+',
      supporting: 'Total rental expenditure'
    }
  }
);
```

### Example 2: Property with Image
```typescript
const propertyCard = createTableCard(
  'prop',
  'Luxury Apartment',
  [
    { label: 'Type', value: '3 BHK' },
    { label: 'Price', value: 'AED 2.5M' },
  ],
  {
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
      'Swimming Pool',
      'Olympic-sized pool with city views',
      [
        { label: 'Access', value: 'Residents only' },
        { label: 'Hours', value: '6 AM - 10 PM' }
      ]
    ),
    // Add 4-6 more amenities...
  ]
);
```

---

## 🎯 Key Features

### Interactive
- ✅ Click/tap to expand/collapse details
- ✅ Smooth transitions and animations
- ✅ Carousel navigation for nested cards
- ✅ Visual indicators for expanded state

### Responsive
- ✅ Horizontal scroll carousel
- ✅ Mobile-friendly touch interactions
- ✅ Proper image scaling and aspect ratios

### Customizable
- ✅ Three card types for different use cases
- ✅ Three content types (text/image/video)
- ✅ Optional subtitles and metadata
- ✅ Flexible detail layouts

### Designed
- ✅ Matches Figma design specifications
- ✅ Glassmorphism effects
- ✅ Proper typography (Instrument Sans, Inter)
- ✅ Consistent spacing and borders

---

## 🎨 Design Specifications

### Card Dimensions
- Width: 300px (fixed)
- Height: Auto (based on content and expanded state)
- Border radius: 32px
- Border: 0.587px white/12% opacity

### Typography
- **Headings:** Instrument Sans (Medium/Bold)
- **Body:** Inter (Regular)
- **Title:** 24px
- **Subtitle:** 14px
- **Details:** 12px (table), 10px (nested)

### Colors
- **Background:** Gradient glassmorphism
- **Text primary:** #fdfdfd (white)
- **Text secondary:** #bdbdbd (light gray)
- **Text tertiary:** #fefae0 (cream)
- **Text muted:** #888 (gray)
- **Accent:** #cc9841 (gold)

---

## 📱 Demo

The `App.tsx` file contains a complete demo with 8 different cards showcasing:
1. Simple text card with table details
2. Large number card (financial)
3. Simple text card with paragraph details
4. Image card with property details
5. Nested cards (amenities carousel)
6. Golden Visa card
7. Permanence card
8. Call-to-action card

Run the app to see all variations in action!

---

## 🛠️ TypeScript Support

Full TypeScript support with type definitions:

```typescript
export type CardContentType = 'text' | 'image' | 'video';
export type DetailType = 'table' | 'simple' | 'nested';

export interface CardData {
  id: string;
  title: string;
  subtitle?: string;
  contentType: CardContentType;
  textContent?: { main?: string; supporting?: string };
  imageContent?: string;
  videoContent?: string;
  detailType: DetailType;
  tableDetails?: TableDetail[];
  simpleDetails?: string;
  nestedCards?: NestedCard[];
}
```

---

## 🎓 Best Practices

### Content Guidelines
- Keep titles under 30 characters
- Use 3-5 table details (max 7)
- Keep simple details to 2-4 lines
- Use 5-7 nested cards for optimal UX

### Performance
- Use imported Figma assets when available
- Lazy load videos for better performance
- Optimize images before use

### Accessibility
- All cards are keyboard accessible
- Proper semantic HTML
- Visual indicators for states

---

## 📚 Additional Resources

- **CardTypes.md** - Detailed explanation of each card type
- **USAGE_GUIDE.md** - Complete usage guide with examples
- **cardExamples.tsx** - Ready-to-use example implementations

---

## 🚀 Next Steps

1. **Customize the data** - Replace sample cards with your actual content
2. **Add more cards** - Create new cards using helper functions
3. **Adjust styling** - Modify colors and spacing to match your brand
4. **Add features** - Extend with filtering, search, or sorting

---

## 💡 Tips

- All Figma assets are properly imported using `figma:asset/...` syntax
- The carousel automatically handles navigation and indicators
- Cards automatically manage their own expansion state
- Use the helper functions to reduce boilerplate code
- Check the examples folder for copy-paste templates

---

**Built with React, TypeScript, and Tailwind CSS v4**
