/**
 * Example usage of card helper functions
 * This file demonstrates how to easily create cards using the helper utilities
 */

import { 
  createTableCard, 
  createSimpleCard, 
  createNestedCard,
  createNestedCardItem,
  createTableDetail,
  CardTemplates 
} from '../utils/cardHelpers';
import { CardData } from '../components/InfoCard';

// Example 1: Create a table card manually
export const exampleTableCard: CardData = createTableCard(
  'example-1',
  'Property Details',
  [
    createTableDetail('Type', '3 BHK Apartment'),
    createTableDetail('Size', '1,800 sqft'),
    createTableDetail('Price', 'AED 2.5M'),
    createTableDetail('Location', 'Dubai Marina'),
  ],
  {
    subtitle: 'Luxury Waterfront Living',
    contentType: 'text',
    textContent: {
      supporting: 'Premium property with stunning marina views'
    }
  }
);

// Example 2: Create a simple text card
export const exampleSimpleCard: CardData = createSimpleCard(
  'example-2',
  'Investment Benefits',
  'Owning property in Dubai offers exceptional ROI with rental yields averaging 6-8% annually. The tax-free environment and strong capital appreciation make it an ideal long-term investment.',
  {
    contentType: 'text',
    textContent: {
      supporting: 'Build wealth through real estate'
    }
  }
);

// Example 3: Create a nested amenities card
export const exampleNestedCard: CardData = createNestedCard(
  'example-3',
  'Luxury Amenities',
  [
    createNestedCardItem(
      'https://images.unsplash.com/photo-1540555700478-4be289fbecef',
      'Infinity Pool',
      'Temperature-controlled infinity pool with panoramic city views and dedicated lanes.',
      [
        createTableDetail('Access', '6 AM - 10 PM'),
        createTableDetail('Features', 'Heated pool')
      ]
    ),
    createNestedCardItem(
      'https://images.unsplash.com/photo-1534438327276-14e5300c3a48',
      'Modern Gym',
      'State-of-the-art fitness center with personal trainers and group classes.',
      [
        createTableDetail('Hours', '24/7'),
        createTableDetail('Trainers', 'Available on request')
      ]
    ),
    createNestedCardItem(
      'https://images.unsplash.com/photo-1600880292203-757bb62b4baf',
      'Business Center',
      'Professional co-working space with high-speed internet and meeting rooms.',
      [
        createTableDetail('Capacity', 'Up to 20 people'),
        createTableDetail('Booking', 'Via app')
      ]
    ),
  ],
  {
    subtitle: 'World-class facilities',
    contentType: 'text',
    textContent: {
      supporting: 'Everything you need for modern living'
    }
  }
);

// Example 4: Using the template helpers
export const examplePropertyListing = CardTemplates.propertyListing(
  'prop-1',
  'The Residences',
  'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00',
  'AED 3.2M',
  '2,100 sqft',
  '4 BHK Penthouse'
);

export const exampleFinancialCard = CardTemplates.financialComparison(
  'finance-1',
  'Monthly Savings',
  'AED\n15,000',
  'Save significantly compared to renting',
  [
    createTableDetail('Rent equivalent', 'AED 25,000/mo'),
    createTableDetail('Mortgage payment', 'AED 18,000/mo'),
    createTableDetail('Monthly savings', 'AED 7,000/mo'),
    createTableDetail('Annual savings', 'AED 84,000'),
  ]
);

export const exampleAmenitiesCard = CardTemplates.amenitiesShowcase(
  'amenities-1',
  'Resort-Style Living',
  'Experience luxury every day',
  [
    createNestedCardItem(
      'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7',
      'Kids Play Area',
      'Safe and fun playground designed for children of all ages with soft surfaces.',
      [
        createTableDetail('Age range', '2-12 years'),
        createTableDetail('Supervision', 'CCTV monitored')
      ]
    ),
    createNestedCardItem(
      'https://images.unsplash.com/photo-1566195992011-5f6b21e539aa',
      'Cinema Room',
      'Private cinema with plush seating and latest audio-visual equipment.',
      [
        createTableDetail('Capacity', '20 seats'),
        createTableDetail('Booking', '2 hours slots')
      ]
    ),
  ]
);

// Export all examples as an array for easy iteration
export const allExamples: CardData[] = [
  exampleTableCard,
  exampleSimpleCard,
  exampleNestedCard,
  examplePropertyListing,
  exampleFinancialCard,
  exampleAmenitiesCard,
];
