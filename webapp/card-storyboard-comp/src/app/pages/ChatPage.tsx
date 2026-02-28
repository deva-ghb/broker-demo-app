import { useState, useRef, useEffect } from 'react';
import { Mic, X, MessageSquare, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router';
import svgPaths from "../../imports/svg-52he9xewlz";
import img2941 from "figma:asset/60d89469c7e4eff58e473b7e3b0b8e1a0538b823.png";

type InputMode = 'voice' | 'text';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export default function ChatPage() {
  const [inputMode, setInputMode] = useState<InputMode>('voice');
  const [isRecording, setIsRecording] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "I'm meeting a potential buyer for Treppan Living Privé. They've been renting in Dubai for six years and are tired of annual rent hikes.",
      sender: 'user',
      timestamp: new Date(Date.now() - 120000)
    },
    {
      id: '2',
      text: "Understood. Based on that profile, they align with. Does this client have a family, and are they looking for a home near international schools?",
      sender: 'ai',
      timestamp: new Date(Date.now() - 60000)
    }
  ]);
  const [textInput, setTextInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMicPress = () => {
    setIsRecording(true);
  };

  const handleMicRelease = () => {
    setIsRecording(false);
    // Simulate adding a voice message
    const newMessage: Message = {
      id: Date.now().toString(),
      text: "Can you tell me more about their interests in the kind of....",
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    
    // Simulate AI response
    setIsResponding(true);
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Based on their interest in luxury lifestyle and yachting, the marina proximity of Treppan Living Privé would be highly appealing. The development offers stunning waterfront views and is within minutes of Dubai Marina's yacht clubs.",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsResponding(false);
    }, 2000);
  };

  const handleTextSubmit = () => {
    if (!textInput.trim()) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      text: textInput,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    setTextInput('');
    
    // Simulate AI response
    setIsResponding(true);
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "That's an excellent point. I can help you highlight the property's key features that address their specific needs. Would you like me to prepare talking points for your meeting?",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsResponding(false);
    }, 2000);
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* Background */}
      <div className="absolute h-full left-0 overflow-clip top-0 w-full">
        {/* Gradient overlay */}
        <div 
          className="absolute bottom-0 h-full left-0 w-full" 
          style={{ backgroundImage: "linear-gradient(180.169deg, rgba(0, 0, 0, 0) 7.7123%, rgb(0, 0, 0) 48.215%)" }} 
        />
        
        {/* Center orb image */}
        <div className="absolute left-1/2 -translate-x-1/2 top-16 md:top-20 w-[290px] h-[290px] md:w-[350px] md:h-[350px]">
          <img 
            alt="" 
            className="absolute inset-0 max-w-none object-cover pointer-events-none w-full h-full" 
            src={img2941} 
          />
        </div>
        
        {/* Animated gradient circles */}
        <div className="absolute bottom-[-467.62px] flex h-[934.618px] items-center justify-center left-[-286px] w-[1058.24px]">
          <div className="flex-none rotate-[14.31deg]">
            <div className="h-[733.754px] relative w-[904.999px]">
              <div className="absolute flex inset-[15.39%_28.93%_0_0] items-center justify-center">
                <div className="flex-none h-[498.815px] rotate-[-65.1deg] w-[452.943px]">
                  <div className="relative w-full h-full">
                    <div className="absolute inset-[-40.1%_-44.16%]">
                      <svg className="block w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 852.943 898.815">
                        <g filter="url(#filter0_f_2_188)" opacity="0.45">
                          <path d={svgPaths.p14901900} fill="#79A8E2" />
                        </g>
                        <defs>
                          <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="898.815" id="filter0_f_2_188" width="852.943" x="0" y="0">
                            <feFlood floodOpacity="0" result="BackgroundImageFix" />
                            <feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape" />
                            <feGaussianBlur result="effect1_foregroundBlur_2_188" stdDeviation="100" />
                          </filter>
                        </defs>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute flex inset-[0_0_25.46%_39.47%] items-center justify-center">
                <div className="flex-none h-[413.092px] rotate-[-65.1deg] w-[411.219px]">
                  <div className="relative w-full h-full">
                    <div className="absolute inset-[-48.42%_-48.64%]">
                      <svg className="block w-full h-full" fill="none" preserveAspectRatio="none" viewBox="0 0 811.219 813.092">
                        <g filter="url(#filter0_f_2_194)" opacity="0.45">
                          <path d={svgPaths.p162ab300} fill="#CC9841" />
                        </g>
                        <defs>
                          <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="813.092" id="filter0_f_2_194" width="811.219" x="-7.51178e-06" y="-2.22522e-06">
                            <feFlood floodOpacity="0" result="BackgroundImageFix" />
                            <feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape" />
                            <feGaussianBlur result="effect1_foregroundBlur_2_194" stdDeviation="100" />
                          </filter>
                        </defs>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages container */}
      <div className="relative z-10 h-full flex flex-col pb-32 pt-[380px] md:pt-[420px]">
        <div className="flex-1 overflow-y-auto px-4 space-y-4 scrollbar-hide">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] md:max-w-[60%] p-4 rounded-2xl ${
                  message.sender === 'user'
                    ? 'ml-auto'
                    : ''
                }`}
                style={{
                  backgroundImage: message.sender === 'user'
                    ? "linear-gradient(99.7224deg, rgba(255, 255, 255, 0.05) 1.7819%, rgba(153, 153, 153, 0.05) 100.06%)"
                    : "linear-gradient(104.656deg, rgba(121, 168, 226, 0.22) 1.7819%, rgba(153, 153, 153, 0.22) 100.06%)"
                }}
              >
                <div 
                  className="absolute border-[0.587px] border-[rgba(255,255,255,0.1)] border-solid inset-0 pointer-events-none rounded-2xl" 
                  aria-hidden="true"
                />
                <p className="font-['Inter:Regular',sans-serif] text-[13px] md:text-[14px] leading-[21px] text-[#fefae0] relative z-10">
                  {message.text}
                </p>
              </div>
            </div>
          ))}
          
          {isResponding && (
            <div className="flex justify-center">
              <p className="font-['Instrument_Sans:Regular',sans-serif] text-[12px] md:text-[13px] text-[#bdbdbd] animate-pulse">
                Responding...
              </p>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Bottom controls */}
      <div className="absolute bottom-0 left-0 right-0 z-20 pb-8 md:pb-12">
        <div className="flex items-center justify-center gap-4 md:gap-6 px-4">
          {/* Text mode button */}
          <button
            onClick={() => setInputMode('text')}
            className={`bg-[rgba(217,217,217,0.2)] backdrop-blur-sm rounded-[22px] w-11 h-11 md:w-12 md:h-12 flex items-center justify-center transition-all ${
              inputMode === 'text' ? 'ring-2 ring-white/40' : ''
            }`}
          >
            <MessageSquare className="w-5 h-5 text-white" />
          </button>

          {/* Voice recording button */}
          <button
            onMouseDown={handleMicPress}
            onMouseUp={handleMicRelease}
            onTouchStart={handleMicPress}
            onTouchEnd={handleMicRelease}
            disabled={inputMode === 'text'}
            className={`relative rounded-full w-16 h-16 md:w-[72px] md:h-[72px] flex items-center justify-center transition-all ${
              inputMode === 'voice'
                ? 'bg-gradient-to-b from-[rgba(255,94,94,0.88)] to-[rgba(153,56,56,0.88)] shadow-[0px_0px_5.818px_0px_rgba(0,0,0,0.25),0px_0px_64px_0px_#ff5e5e] opacity-100'
                : 'bg-gray-600 opacity-30 cursor-not-allowed'
            } ${isRecording ? 'scale-110' : 'scale-100'}`}
          >
            <div className="absolute inset-0 pointer-events-none rounded-full shadow-[inset_0px_0px_2.909px_0px_#ff5e5e]" />
            <Mic className="w-7 h-7 md:w-8 md:h-8 text-white relative z-10" />
            
            {isRecording && (
              <div className="absolute inset-0 rounded-full bg-red-500/30 animate-pulse" />
            )}
          </button>

          {/* Close/Send button */}
          <button
            onClick={() => {
              if (inputMode === 'text' && textInput.trim()) {
                handleTextSubmit();
              }
            }}
            className="bg-[rgba(217,217,217,0.2)] backdrop-blur-sm rounded-[22px] w-11 h-11 md:w-12 md:h-12 flex items-center justify-center transition-all hover:bg-[rgba(217,217,217,0.3)]"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Text input (shown when text mode is active) */}
        {inputMode === 'text' && (
          <div className="mt-4 px-4 animate-fadeIn">
            <div className="max-w-2xl mx-auto relative">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleTextSubmit();
                  }
                }}
                placeholder="Type your message..."
                className="w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl px-6 py-4 text-white placeholder-white/50 font-['Inter:Regular',sans-serif] text-[14px] focus:outline-none focus:ring-2 focus:ring-white/40"
              />
            </div>
          </div>
        )}

        {/* Home indicator */}
        <div className="flex justify-center mt-6">
          <div className="bg-[#7c7c7c] h-[5px] rounded-full w-[100px] md:w-[139px]" />
        </div>
      </div>

      {/* Back button */}
      <Link 
        to="/" 
        className="absolute top-6 md:top-8 left-4 md:left-8 z-30 bg-white/10 backdrop-blur-md rounded-full p-3 md:p-4 border border-white/20 hover:bg-white/20 transition-all group"
      >
        <ArrowLeft className="w-5 h-5 md:w-6 md:h-6 text-white" />
        <div className="absolute inset-0 bg-white/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
      </Link>

      {/* AI Assistant indicator */}
      <div className="absolute top-6 md:top-8 left-1/2 -translate-x-1/2 z-30">
        <div className="bg-white/10 backdrop-blur-md rounded-full px-5 md:px-8 py-2 md:py-3 border border-white/20">
          <p className="font-['Instrument_Sans:Medium',sans-serif] text-[12px] md:text-[14px] text-white/90">
            AI Broker Assistant
          </p>
        </div>
      </div>
    </div>
  );
}