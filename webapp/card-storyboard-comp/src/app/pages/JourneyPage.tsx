import { useState, useEffect, useCallback } from 'react';
import { InfoCard, CardData } from '../components/InfoCard';
import { ChevronLeft, ChevronRight, MessageSquare } from 'lucide-react';
import { Link } from 'react-router';
import imgTreppan from "figma:asset/ddeb673371e522aebf64a94ef5d74319a5666459.png";
import imgFamilyWellness from "figma:asset/45a8b967293c27de641e52e773659b769085f341.png";

// Sample card data demonstrating all three types
const journeyCards: CardData[] = [
  {
    id: '1',
    title: 'Permanent Address Found',
    contentType: 'text',
    textContent: {
      supporting: 'The security of a permanent home provides a foundation for life. Ownership transforms a residence into a lasting legacy.'
    },
    detailType: 'table',
    tableDetails: [
      { label: 'Market Status', value: 'Dubai Residential' },
      { label: 'Tenure', value: '100% Freehold' },
      { label: 'Availability', value: 'Limited Private Units' }
    ]
  },
  
  {
    id: '2',
    title: 'The Cost of Waiting',
    contentType: 'text',
    textContent: {
      main: 'AED\n600,000+',
      supporting: 'Total rental expenditure over five years creates zero wealth.'
    },
    detailType: 'table',
    tableDetails: [
      { label: 'Avg. annual rent', value: 'AED 120,000' },
      { label: '5-year total rent', value: 'AED 600,000+' },
      { label: 'Equity built (renting)', value: 'AED 0' },
      { label: 'Potential Equity (owned)', value: 'AED 680,000+' }
    ]
  },
  
  {
    id: '3',
    title: 'Seamless Daily Transition',
    contentType: 'text',
    textContent: {
      supporting: 'Maintain the same routine and commute while building personal wealth.'
    },
    detailType: 'simple',
    simpleDetails: 'Maintain the same routine and commute while building personal wealth. The daily rhythm remains, but the financial outcome changes. Your lifestyle stays uninterrupted while equity accumulates month by month.'
  },
  
  {
    id: '4',
    title: 'Treppan Living Privé',
    subtitle: 'Q3 2026 Handover',
    contentType: 'image',
    imageContent: imgTreppan,
    detailType: 'table',
    tableDetails: [
      { label: 'Type', value: '2 BHK + Study' },
      { label: 'Size', value: '1,250 - 1,480 sqft' },
      { label: 'Price', value: 'AED 2.1M - 2.4M' },
      { label: 'Schools', value: 'Within 10 minutes' },
      { label: 'Developer', value: 'Fakhruddin Properties' }
    ]
  },
  
  {
    id: '5',
    title: 'Premium Amenities',
    subtitle: 'World-class facilities designed for your comfort',
    contentType: 'text',
    textContent: {
      supporting: 'Exclusive facilities that enhance your lifestyle every day.'
    },
    detailType: 'nested',
    nestedCards: [
      {
        image: imgFamilyWellness,
        title: 'Family Wellness',
        description: "A dedicated space for relaxation with a separate children's section.",
        details: [
          { label: 'Access', value: 'Residents only' },
          { label: 'Safety', value: 'Lifeguard monitored' }
        ]
      },
      {
        image: 'https://images.unsplash.com/photo-1771586791190-97ed536c54af?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBmaXRuZXNzJTIwZ3ltJTIwZXF1aXBtZW50fGVufDF8fHx8MTc3MjI5NjgzNnww&ixlib=rb-4.1.0&q=80&w=1080',
        title: 'State-of-the-Art Gym',
        description: 'Fully equipped fitness center with premium equipment and personal training available.',
        details: [
          { label: 'Hours', value: '24/7 Access' },
          { label: 'Equipment', value: 'Premium grade' }
        ]
      },
      {
        image: 'https://images.unsplash.com/photo-1562839938-ef837ead7478?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcGElMjB3ZWxsbmVzcyUyMHJlbGF4YXRpb258ZW58MXx8fHwxNzcyMjQwODg0fDA&ixlib=rb-4.1.0&q=80&w=1080',
        title: 'Wellness Spa',
        description: 'Luxurious spa facilities including sauna, steam room, and massage therapy rooms.',
        details: [
          { label: 'Booking', value: 'Via concierge' },
          { label: 'Services', value: 'Professional staff' }
        ]
      },
      {
        image: 'https://images.unsplash.com/photo-1749759426604-063b5effd7a1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb29mdG9wJTIwdGVycmFjZSUyMGdhcmRlbnxlbnwxfHx8fDE3NzIxODg5MTh8MA&ixlib=rb-4.1.0&q=80&w=1080',
        title: 'Sky Garden',
        description: 'Rooftop terrace with landscaped gardens, BBQ areas, and stunning city views.',
        details: [
          { label: 'Features', value: 'BBQ & Dining' },
          { label: 'Capacity', value: 'Group bookings' }
        ]
      },
      {
        image: 'https://images.unsplash.com/photo-1759038085950-1234ca8f5fed?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb25jaWVyZ2UlMjBzZXJ2aWNlJTIwaG90ZWx8ZW58MXx8fHwxNzcyMjk2ODM3fDA&ixlib=rb-4.1.0&q=80&w=1080',
        title: 'Concierge Service',
        description: '24/7 professional concierge to assist with reservations, deliveries, and services.',
        details: [
          { label: 'Availability', value: '24/7' },
          { label: 'Languages', value: 'Multi-lingual' }
        ]
      }
    ]
  },
  
  {
    id: '6',
    title: '10-Year Residency',
    contentType: 'text',
    textContent: {
      main: 'Golden\nVisa',
      supporting: 'Ownership above AED 2M qualifies for the UAE Golden Visa for the primary holder and family.'
    },
    detailType: 'table',
    tableDetails: [
      { label: 'Visa Term', value: '10-Year Renewable' },
      { label: 'Family', value: 'Spouse & Children included' },
      { label: 'Independence', value: 'Employer independent' }
    ]
  },
  
  {
    id: '7',
    title: 'Unconditional Permanence',
    contentType: 'text',
    textContent: {
      supporting: 'Financial prudence meets long-term peace of mind.'
    },
    detailType: 'simple',
    simpleDetails: 'Financial prudence meets long-term peace of mind. Every monthly payment contributes to a tangible family asset. Build equity while maintaining your current lifestyle without compromise.'
  },
  
  {
    id: '8',
    title: 'Request Private Briefing',
    contentType: 'text',
    textContent: {
      supporting: 'A matched shortlist and detailed financial breakdown are prepared. Private 20-minute walkthroughs are available.'
    },
    detailType: 'simple',
    simpleDetails: 'Schedule a personalized consultation to review curated property options that match your specific requirements. Our team will prepare a comprehensive financial analysis and arrange private viewings at your convenience.'
  }
];

export default function JourneyPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  const currentCard = journeyCards[currentIndex];
  const totalCards = journeyCards.length;

  // Minimum swipe distance (in px)
  const minSwipeDistance = 50;

  const handleNext = () => {
    if (currentIndex < totalCards - 1 && !isTransitioning) {
      setIsTransitioning(true);
      setExpandedCardId(null);
      setTimeout(() => {
        setCurrentIndex(currentIndex + 1);
        setIsTransitioning(false);
      }, 300);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0 && !isTransitioning) {
      setIsTransitioning(true);
      setExpandedCardId(null);
      setTimeout(() => {
        setCurrentIndex(currentIndex - 1);
        setIsTransitioning(false);
      }, 300);
    }
  };

  const handleCardToggle = () => {
    setExpandedCardId(expandedCardId === currentCard.id ? null : currentCard.id);
  };

  // Touch handlers for swipe
  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe) {
      handleNext();
    }
    if (isRightSwipe) {
      handlePrevious();
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        handleNext();
      } else if (e.key === 'ArrowLeft') {
        handlePrevious();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, isTransitioning]); // Added dependencies

  return (
    <div 
      className="relative w-full h-screen bg-black overflow-hidden"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {/* Animated background gradient */}
      <div 
        className="absolute inset-0 transition-all duration-1000" 
        style={{ 
          backgroundImage: 'linear-gradient(180.366deg, rgba(0, 0, 0, 0) 7.8363%, rgb(0, 0, 0) 48.22%)' 
        }} 
      />
      
      {/* Decorative blurred circles that animate based on card index */}
      <div 
        className="absolute top-[15%] left-[-10%] w-[400px] h-[400px] md:w-[600px] md:h-[600px] opacity-25 transition-all duration-1000"
        style={{
          transform: `translate(${currentIndex * 50}px, ${currentIndex * 30}px) scale(${1 + currentIndex * 0.1})`
        }}
      >
        <div className="w-full h-full rounded-full bg-[#79A8E2] blur-[120px]" />
      </div>
      <div 
        className="absolute top-[20%] right-[-10%] w-[350px] h-[350px] md:w-[500px] md:h-[500px] opacity-25 transition-all duration-1000"
        style={{
          transform: `translate(${-currentIndex * 40}px, ${currentIndex * 40}px) scale(${1 + currentIndex * 0.08})`
        }}
      >
        <div className="w-full h-full rounded-full bg-[#CC9841] blur-[120px]" />
      </div>

      {/* Main content container */}
      <div className="relative z-10 flex items-center justify-center h-full px-4 md:px-8 lg:px-16">
        {/* Previous button - Translucent left arrow */}
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className={`absolute left-2 md:left-8 lg:left-16 top-1/2 -translate-y-1/2 z-20 group transition-all duration-500 ${
            currentIndex === 0 
              ? 'opacity-0 pointer-events-none' 
              : 'opacity-30 hover:opacity-100'
          }`}
        >
          <div className="relative">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-white/20 rounded-full blur-2xl scale-150 group-hover:scale-[2] transition-transform duration-500" />
            
            {/* Arrow button */}
            <div className="relative bg-white/10 backdrop-blur-md rounded-full w-12 h-12 md:w-16 md:h-16 flex items-center justify-center border border-white/20 group-hover:bg-white/20 transition-all duration-300">
              <ChevronLeft className="w-6 h-6 md:w-8 md:h-8 text-white" />
            </div>
          </div>
        </button>

        {/* Card container - Responsive width */}
        <div className="w-full max-w-[95vw] sm:max-w-[540px] md:max-w-[680px] lg:max-w-[800px] xl:max-w-[920px] min-h-[600px] flex items-center justify-center">
          <InfoCard
            card={currentCard}
            isExpanded={expandedCardId === currentCard.id}
            onToggle={handleCardToggle}
            isActive={!isTransitioning}
          />
        </div>

        {/* Next button - Translucent right arrow */}
        <button
          onClick={handleNext}
          disabled={currentIndex === totalCards - 1}
          className={`absolute right-2 md:right-8 lg:right-16 top-1/2 -translate-y-1/2 z-20 group transition-all duration-500 ${
            currentIndex === totalCards - 1 
              ? 'opacity-0 pointer-events-none' 
              : 'opacity-30 hover:opacity-100'
          }`}
        >
          <div className="relative">
            {/* Glow effect */}
            <div className="absolute inset-0 bg-white/20 rounded-full blur-2xl scale-150 group-hover:scale-[2] transition-transform duration-500" />
            
            {/* Arrow button */}
            <div className="relative bg-white/10 backdrop-blur-md rounded-full w-12 h-12 md:w-16 md:h-16 flex items-center justify-center border border-white/20 group-hover:bg-white/20 transition-all duration-300">
              <ChevronRight className="w-6 h-6 md:w-8 md:h-8 text-white" />
            </div>
          </div>
        </button>
      </div>

      {/* Journey progress indicator */}
      <div className="absolute bottom-8 md:bottom-12 left-0 right-0 z-20">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 md:gap-3 mb-4 md:mb-6 px-4">
          {journeyCards.map((card, index) => (
            <button
              key={card.id}
              onClick={() => {
                if (!isTransitioning) {
                  setIsTransitioning(true);
                  setExpandedCardId(null);
                  setTimeout(() => {
                    setCurrentIndex(index);
                    setIsTransitioning(false);
                  }, 300);
                }
              }}
              className={`h-1.5 md:h-2 rounded-full transition-all duration-500 ${
                index === currentIndex
                  ? 'w-10 md:w-12 bg-white shadow-lg shadow-white/50'
                  : index < currentIndex
                  ? 'w-1.5 md:w-2 bg-white/60'
                  : 'w-1.5 md:w-2 bg-white/30'
              }`}
            />
          ))}
        </div>

        {/* Card counter */}
        <div className="flex justify-center">
          <div className="bg-white/10 backdrop-blur-md rounded-full px-4 md:px-6 py-1.5 md:py-2 border border-white/20">
            <p className="font-['Inter:Regular',sans-serif] text-[12px] md:text-[14px] text-white">
              <span className="font-semibold">{currentIndex + 1}</span>
              <span className="text-white/60"> / {totalCards}</span>
            </p>
          </div>
        </div>

        {/* Home indicator bar */}
        <div className="flex justify-center mt-4 md:mt-6">
          <div className="bg-white/40 h-[5px] w-[100px] md:w-[139px] rounded-full" />
        </div>
      </div>

      {/* Journey milestone indicator (top) */}
      <div className="absolute top-6 md:top-8 left-0 right-0 z-20 flex justify-center px-4">
        <div className="bg-white/10 backdrop-blur-md rounded-full px-5 md:px-8 py-2 md:py-3 border border-white/20">
          <p className="font-['Instrument_Sans:Medium',sans-serif] text-[12px] md:text-[14px] text-white/90">
            Your Property Journey
          </p>
        </div>
      </div>

      {/* Chat button - Fixed position */}
      <Link 
        to="/chat"
        className="absolute top-6 md:top-8 right-4 md:right-8 z-30 bg-white/10 backdrop-blur-md rounded-full p-3 md:p-4 border border-white/20 hover:bg-white/20 transition-all group"
      >
        <MessageSquare className="w-5 h-5 md:w-6 md:h-6 text-white" />
        <div className="absolute inset-0 bg-white/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
      </Link>

      {/* Swipe hint (only on first card) */}
      {currentIndex === 0 && !expandedCardId && (
        <div className="absolute bottom-28 md:bottom-32 right-6 md:right-12 z-10 animate-pulse">
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md rounded-full px-3 md:px-4 py-1.5 md:py-2 border border-white/20">
            <p className="font-['Inter:Regular',sans-serif] text-[11px] md:text-[12px] text-white/80">
              Swipe to continue
            </p>
            <ChevronRight className="w-3 h-3 md:w-4 md:h-4 text-white/80" />
          </div>
        </div>
      )}
    </div>
  );
}