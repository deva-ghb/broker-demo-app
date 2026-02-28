import { CardData, TableDetail, NestedCard } from '../components/InfoCard';

/**
 * Helper functions to create card data objects
 */

/**
 * Create a table-type card with key-value details
 */
export function createTableCard(
  id: string,
  title: string,
  details: TableDetail[],
  options?: {
    subtitle?: string;
    contentType?: 'text' | 'image' | 'video';
    textContent?: { main?: string; supporting?: string };
    imageContent?: string;
    videoContent?: string;
  }
): CardData {
  return {
    id,
    title,
    subtitle: options?.subtitle,
    contentType: options?.contentType || 'text',
    textContent: options?.textContent,
    imageContent: options?.imageContent,
    videoContent: options?.videoContent,
    detailType: 'table',
    tableDetails: details,
  };
}

/**
 * Create a simple text card with descriptive details
 */
export function createSimpleCard(
  id: string,
  title: string,
  simpleDetails: string,
  options?: {
    subtitle?: string;
    contentType?: 'text' | 'image' | 'video';
    textContent?: { main?: string; supporting?: string };
    imageContent?: string;
    videoContent?: string;
  }
): CardData {
  return {
    id,
    title,
    subtitle: options?.subtitle,
    contentType: options?.contentType || 'text',
    textContent: options?.textContent,
    imageContent: options?.imageContent,
    videoContent: options?.videoContent,
    detailType: 'simple',
    simpleDetails,
  };
}

/**
 * Create a nested card type with sub-cards (e.g., amenities)
 */
export function createNestedCard(
  id: string,
  title: string,
  nestedCards: NestedCard[],
  options?: {
    subtitle?: string;
    contentType?: 'text' | 'image' | 'video';
    textContent?: { main?: string; supporting?: string };
    imageContent?: string;
    videoContent?: string;
  }
): CardData {
  return {
    id,
    title,
    subtitle: options?.subtitle,
    contentType: options?.contentType || 'text',
    textContent: options?.textContent,
    imageContent: options?.imageContent,
    videoContent: options?.videoContent,
    detailType: 'nested',
    nestedCards,
  };
}

/**
 * Create a nested card item (for use within nested cards)
 */
export function createNestedCardItem(
  image: string,
  title: string,
  description: string,
  details?: TableDetail[]
): NestedCard {
  return {
    image,
    title,
    description,
    details,
  };
}

/**
 * Create a table detail item
 */
export function createTableDetail(label: string, value: string): TableDetail {
  return { label, value };
}

/**
 * Example usage templates
 */
export const CardTemplates = {
  /**
   * Template for a property listing card
   */
  propertyListing: (
    id: string,
    title: string,
    image: string,
    price: string,
    size: string,
    type: string
  ): CardData => createTableCard(
    id,
    title,
    [
      createTableDetail('Type', type),
      createTableDetail('Size', size),
      createTableDetail('Price', price),
    ],
    {
      contentType: 'image',
      imageContent: image,
    }
  ),

  /**
   * Template for a financial comparison card
   */
  financialComparison: (
    id: string,
    title: string,
    mainAmount: string,
    description: string,
    breakdown: TableDetail[]
  ): CardData => createTableCard(
    id,
    title,
    breakdown,
    {
      contentType: 'text',
      textContent: {
        main: mainAmount,
        supporting: description,
      },
    }
  ),

  /**
   * Template for an amenities showcase card
   */
  amenitiesShowcase: (
    id: string,
    title: string,
    subtitle: string,
    amenities: NestedCard[]
  ): CardData => createNestedCard(
    id,
    title,
    amenities,
    {
      subtitle,
      contentType: 'text',
      textContent: {
        supporting: 'Exclusive facilities that enhance your lifestyle.',
      },
    }
  ),
};
