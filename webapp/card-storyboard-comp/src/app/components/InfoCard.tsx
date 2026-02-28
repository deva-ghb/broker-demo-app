import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

// Type definitions
export type CardContentType = 'text' | 'image' | 'video';

export type DetailType = 'table' | 'simple' | 'nested';

export interface TableDetail {
  label: string;
  value: string;
}

export interface NestedCard {
  image: string;
  title: string;
  description: string;
  details?: TableDetail[];
}

export interface CardData {
  id: string;
  title: string;
  subtitle?: string;
  contentType: CardContentType;
  textContent?: {
    main?: string;
    supporting?: string;
  };
  imageContent?: string;
  videoContent?: string;
  detailType: DetailType;
  tableDetails?: TableDetail[];
  simpleDetails?: string;
  nestedCards?: NestedCard[];
}

interface InfoCardProps {
  card: CardData;
  isExpanded?: boolean;
  onToggle?: () => void;
  isActive?: boolean;
}

export function InfoCard({ card, isExpanded = false, onToggle, isActive = false }: InfoCardProps) {
  const [currentNestedIndex, setCurrentNestedIndex] = useState(0);

  const renderMainContent = () => {
    switch (card.contentType) {
      case 'text':
        return (
          <div className="flex-1 flex flex-col items-center justify-center px-6 md:px-9 py-6 md:py-9">
            {card.textContent?.main && (
              <p className="font-['Instrument_Sans:Bold',sans-serif] font-bold text-[48px] md:text-[60px] lg:text-[72px] leading-[48px] md:leading-[60px] lg:leading-[72px] text-[#cc9841] text-center whitespace-pre-wrap">
                {card.textContent.main}
              </p>
            )}
            {card.textContent?.supporting && (
              <p className="font-['Inter:Regular',sans-serif] text-[14px] md:text-[16px] lg:text-[18px] leading-[22px] md:leading-[24px] lg:leading-[28px] text-[#fefae0] text-center mt-4 md:mt-6 max-w-[90%] md:max-w-[400px] lg:max-w-[500px]">
                {card.textContent.supporting}
              </p>
            )}
          </div>
        );
      
      case 'image':
        return (
          <div className="flex-1 p-4 md:p-6">
            <div className="relative w-full h-full max-h-[350px] md:max-h-[450px] lg:max-h-[500px] rounded-[24px] md:rounded-[32px] overflow-hidden">
              <img 
                src={card.imageContent} 
                alt={card.title}
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        );
      
      case 'video':
        return (
          <div className="flex-1 p-4 md:p-6">
            <div className="relative w-full h-full max-h-[350px] md:max-h-[450px] lg:max-h-[500px] rounded-[24px] md:rounded-[32px] overflow-hidden bg-black/20">
              <video 
                src={card.videoContent}
                className="w-full h-full object-cover"
                controls
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  const renderDetails = () => {
    if (!isExpanded) return null;

    switch (card.detailType) {
      case 'table':
        return (
          <div className="px-12 pb-8 space-y-4 animate-fadeIn">
            {card.tableDetails?.map((detail, index) => (
              <div key={index} className="flex justify-between items-start">
                <p className="font-['Inter:Regular',sans-serif] text-[14px] text-[#888]">
                  {detail.label}
                </p>
                <p className="font-['Inter:Regular',sans-serif] text-[14px] text-[#fefae0] text-right">
                  {detail.value}
                </p>
              </div>
            ))}
          </div>
        );
      
      case 'simple':
        return (
          <div className="px-12 pb-8 animate-fadeIn">
            <p className="font-['Inter:Regular',sans-serif] text-[14px] leading-[24px] text-[#fefae0]">
              {card.simpleDetails}
            </p>
          </div>
        );
      
      case 'nested':
        if (!card.nestedCards || card.nestedCards.length === 0) return null;
        
        const currentCard = card.nestedCards[currentNestedIndex];
        const totalCards = card.nestedCards.length;
        
        return (
          <div className="px-6 pb-8 animate-fadeIn">
            <div className="relative">
              {/* Nested card image - FIXED HEIGHT */}
              <div className="relative w-full h-[280px] rounded-[32px] overflow-hidden mb-6">
                <img 
                  src={currentCard.image} 
                  alt={currentCard.title}
                  className="w-full h-full object-cover"
                />
                
                {/* Navigation buttons */}
                {totalCards > 1 && (
                  <>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCurrentNestedIndex((prev) => 
                          prev === 0 ? totalCards - 1 : prev - 1
                        );
                      }}
                      className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm rounded-full w-12 h-12 flex items-center justify-center hover:bg-white/30 transition-all"
                    >
                      <ChevronLeft className="w-6 h-6 text-white" />
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCurrentNestedIndex((prev) => 
                          prev === totalCards - 1 ? 0 : prev + 1
                        );
                      }}
                      className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 backdrop-blur-sm rounded-full w-12 h-12 flex items-center justify-center hover:bg-white/30 transition-all"
                    >
                      <ChevronRight className="w-6 h-6 text-white" />
                    </button>
                  </>
                )}
              </div>
              
              {/* Nested card details */}
              <div className="bg-black/40 backdrop-blur-sm rounded-[24px] p-6 space-y-4">
                <p className="font-['Inter:Regular',sans-serif] text-[13px] leading-[20px] text-[#fefae0]">
                  {currentCard.description}
                </p>
                
                {currentCard.details && currentCard.details.length > 0 && (
                  <div className="space-y-2">
                    {currentCard.details.map((detail, index) => (
                      <div key={index} className="flex justify-between items-start">
                        <p className="font-['Inter:Regular',sans-serif] text-[11px] leading-[16px] text-[#888]">
                          {detail.label}
                        </p>
                        <p className="font-['Inter:Regular',sans-serif] text-[11px] leading-[16px] text-[#fefae0]">
                          {detail.value}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Carousel indicators */}
              {totalCards > 1 && (
                <div className="flex justify-center gap-2 mt-4">
                  {Array.from({ length: totalCards }).map((_, index) => (
                    <div
                      key={index}
                      className={`h-1.5 rounded-full transition-all ${
                        index === currentNestedIndex 
                          ? 'w-8 bg-white' 
                          : 'w-1.5 bg-white/30'
                      }`}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div
      onClick={onToggle}
      className={`relative w-full max-w-[600px] lg:max-w-[800px] xl:max-w-[920px] mx-auto flex-shrink-0 cursor-pointer transition-all duration-500 ${
        isActive ? 'scale-100 opacity-100' : 'scale-95 opacity-0 pointer-events-none'
      }`}
    >
      {/* Card background with gradient */}
      <div 
        className="relative rounded-[32px] md:rounded-[48px] overflow-hidden backdrop-blur-xl"
        style={{
          background: 'linear-gradient(-43.7814deg, rgba(255, 255, 255, 0.44) 7.5746%, rgba(0, 0, 0, 0.44) 93.518%)',
          opacity: 0.45
        }}
      >
        {/* Border */}
        <div className="absolute inset-0 rounded-[32px] md:rounded-[48px] border-[0.8px] border-white/12" />
        
        {/* Content */}
        <div className="relative rounded-[32px] md:rounded-[48px] overflow-hidden">
          {/* Title section */}
          <div className="px-8 md:px-12 pt-8 md:pt-12 pb-4 md:pb-6">
            <h3 className="font-['Instrument_Sans:Medium',sans-serif] font-medium text-[28px] md:text-[36px] lg:text-[42px] leading-[32px] md:leading-[40px] lg:leading-[48px] text-[#fdfdfd] text-center whitespace-pre-wrap">
              {card.title}
            </h3>
            {card.subtitle && (
              <p className="font-['Instrument_Sans:Regular',sans-serif] text-[16px] md:text-[18px] lg:text-[20px] leading-[22px] md:leading-[24px] lg:leading-[28px] text-[#bdbdbd] text-center mt-2 md:mt-3">
                {card.subtitle}
              </p>
            )}
          </div>
          
          {/* Main content */}
          {renderMainContent()}
          
          {/* Details section */}
          {renderDetails()}
          
          {/* Tap indicator */}
          {!isExpanded && (
            <div className="px-8 md:px-12 pb-6 md:pb-8 flex justify-center">
              <div className="animate-bounce">
                <p className="font-['Inter:Regular',sans-serif] text-[11px] md:text-[12px] text-white/60">
                  Tap to explore
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}