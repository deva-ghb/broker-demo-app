import svgPaths from "./svg-52he9xewlz";
import img2941 from "figma:asset/60d89469c7e4eff58e473b7e3b0b8e1a0538b823.png";

function Overlay() {
  return <div className="absolute bottom-0 h-[852px] left-0 w-[393px]" data-name="Overlay" style={{ backgroundImage: "linear-gradient(180.169deg, rgba(0, 0, 0, 0) 7.7123%, rgb(0, 0, 0) 48.215%)" }} />;
}

function Background() {
  return (
    <div className="absolute h-[852px] left-0 overflow-clip top-0 w-[393px]" data-name="Background">
      <Overlay />
      <div className="absolute left-[52px] size-[290px] top-[64px]" data-name="294 1">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={img2941} />
      </div>
      <div className="absolute bottom-[-467.62px] flex h-[934.618px] items-center justify-center left-[-286px] w-[1058.24px]" style={{ "--transform-inner-width": "1200", "--transform-inner-height": "37" } as React.CSSProperties}>
        <div className="flex-none rotate-[14.31deg]">
          <div className="h-[733.754px] relative w-[904.999px]" data-name="BG Mesh Gradient 1">
            <div className="absolute flex inset-[15.39%_28.93%_0_0] items-center justify-center">
              <div className="flex-none h-[498.815px] rotate-[-65.1deg] w-[452.943px]">
                <div className="relative size-full">
                  <div className="absolute inset-[-40.1%_-44.16%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 852.943 898.815">
                      <g filter="url(#filter0_f_2_188)" id="Ellipse 376" opacity="0.45">
                        <path d={svgPaths.p14901900} fill="var(--fill-0, #79A8E2)" />
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
                <div className="relative size-full">
                  <div className="absolute inset-[-48.42%_-48.64%]">
                    <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 811.219 813.092">
                      <g filter="url(#filter0_f_2_194)" id="Ellipse 377" opacity="0.45">
                        <path d={svgPaths.p162ab300} fill="var(--fill-0, #CC9841)" />
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
  );
}

function Paragraph() {
  return (
    <div className="content-stretch flex items-center justify-center relative shrink-0 w-full" data-name="Paragraph">
      <p className="font-['Inter:Regular',sans-serif] font-normal leading-[21px] not-italic relative shrink-0 text-[#fefae0] text-[12px] w-[240px] whitespace-pre-wrap">{`I'm pitching the 52nd-floor penthouse to a Russian investor named Igor who loves yachting and the luxury lifestyle. He's looking for prestige`}</p>
    </div>
  );
}

function Container() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-[calc(20%+9.4px)] p-[16px] rounded-[16px] top-[336px] w-[288.779px]" data-name="Container" style={{ backgroundImage: "linear-gradient(99.7224deg, rgba(255, 255, 255, 0.05) 1.7819%, rgba(153, 153, 153, 0.05) 100.06%)" }}>
      <div aria-hidden="true" className="absolute border-[0.587px] border-[rgba(255,255,255,0.1)] border-solid inset-0 pointer-events-none rounded-[16px]" />
      <Paragraph />
    </div>
  );
}

function Paragraph1() {
  return (
    <div className="content-stretch flex items-center justify-center relative shrink-0 w-full" data-name="Paragraph">
      <p className="font-['Inter:Regular',sans-serif] font-normal leading-[21px] not-italic relative shrink-0 text-[#fefae0] text-[12px] w-[240px] whitespace-pre-wrap">Can you tell me more about their interests in the kind of....</p>
    </div>
  );
}

function Container1() {
  return (
    <div className="absolute content-stretch flex flex-col items-start left-[16px] p-[16px] rounded-[16px] top-[469px] w-[288.779px]" data-name="Container" style={{ backgroundImage: "linear-gradient(105.034deg, rgba(121, 168, 226, 0.22) 1.7819%, rgba(153, 153, 153, 0.22) 100.06%)" }}>
      <div aria-hidden="true" className="absolute border-[0.587px] border-[rgba(255,255,255,0.1)] border-solid inset-0 pointer-events-none rounded-[16px]" />
      <Paragraph1 />
    </div>
  );
}

function Frame() {
  return (
    <div className="absolute bg-gradient-to-b content-stretch flex from-[rgba(255,94,94,0.88)] items-start left-[calc(40%+7.3px)] opacity-44 p-[14.545px] rounded-[32px] shadow-[0px_0px_5.818px_0px_rgba(0,0,0,0.25),0px_0px_64px_0px_#ff5e5e] size-[64px] to-[rgba(153,56,56,0.88)] top-[724px]">
      <div className="content-stretch flex items-center justify-center relative rounded-[5.818px] shrink-0 size-[34.909px]" data-name="IconBase">
        <div className="flex-[1_0_0] h-full min-h-px min-w-px relative" data-name="Weight=Regular">
          <div className="absolute inset-[6.25%_18.75%]" data-name="Vector">
            <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 21.8182 30.5455">
              <path d={svgPaths.p1668f0e0} fill="var(--fill-0, #FDFDFD)" id="Vector" />
            </svg>
          </div>
        </div>
      </div>
      <div className="absolute inset-0 pointer-events-none rounded-[inherit] shadow-[inset_0px_0px_2.909px_0px_#ff5e5e]" />
    </div>
  );
}

function Frame1() {
  return (
    <div className="absolute bg-[rgba(217,217,217,0.2)] content-stretch flex items-center justify-center left-[calc(80%+1.6px)] p-[10px] rounded-[22px] size-[44px] top-[734px]">
      <div className="content-stretch flex items-center justify-center relative rounded-[12px] shrink-0 size-[20px]" data-name="IconBase">
        <div className="flex-[1_0_0] h-full min-h-px min-w-px relative" data-name="Weight=Regular">
          <div className="absolute inset-[18.75%]" data-name="Vector">
            <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 12.5007 12.5007">
              <path d={svgPaths.p3e5fcf0} fill="var(--fill-0, #FDFDFD)" id="Vector" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

function Frame2() {
  return (
    <div className="absolute bg-[rgba(217,217,217,0.2)] content-stretch flex items-center justify-center left-[33px] p-[10px] rounded-[22px] size-[44px] top-[734px]">
      <div className="content-stretch flex items-center justify-center relative rounded-[12px] shrink-0 size-[20px]" data-name="IconBase">
        <div className="flex-[1_0_0] h-full min-h-px min-w-px relative" data-name="Weight=Regular">
          <div className="absolute inset-[18.75%_6.25%]" data-name="Vector">
            <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 17.5 12.5">
              <path d={svgPaths.p1bc41500} fill="var(--fill-0, #FDFDFD)" id="Vector" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function BrokerInput() {
  return (
    <div className="bg-black content-stretch flex flex-col items-center justify-end relative size-full" data-name="Broker Input">
      <Background />
      <div className="content-stretch flex flex-col items-center justify-center px-[16px] py-[12px] relative shrink-0 w-[393px]" data-name="iOS Home Indicator">
        <div className="bg-[#7c7c7c] h-[5px] rounded-[100px] shrink-0 w-[139px]" data-name="Home Indicator" />
      </div>
      <Container />
      <Container1 />
      <Frame />
      <p className="-translate-x-1/2 absolute font-['Instrument_Sans:Regular',sans-serif] font-normal leading-[20px] left-[196.5px] text-[#bdbdbd] text-[12px] text-center top-[679px] w-[393px] whitespace-pre-wrap" style={{ fontVariationSettings: "'wdth' 100" }}>
        Responding...
      </p>
      <Frame1 />
      <Frame2 />
    </div>
  );
}