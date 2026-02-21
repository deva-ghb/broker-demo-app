#!/bin/bash

# Voice Persona Builder - Setup Verification Script
# This script checks if everything is properly configured

echo "🔍 Voice Persona Builder - Setup Verification"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to print check result
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} $2"
        ((CHECKS_FAILED++))
    fi
}

# 1. Check if .env file exists
echo "1️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    check_result 0 ".env file exists"

    # Check if OPENAI_API_KEY is set
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        check_result 0 "OPENAI_API_KEY is configured"
    else
        check_result 1 "OPENAI_API_KEY is not set (required for voice)"
        echo -e "   ${YELLOW}→${NC} Add your OpenAI API key to .env file"
    fi
else
    check_result 1 ".env file not found"
    echo -e "   ${YELLOW}→${NC} Copy .env.example to .env and configure"
fi
echo ""

# 2. Check Python dependencies
echo "2️⃣  Checking Python dependencies..."
if command -v pip &> /dev/null; then
    check_result 0 "pip is installed"

    # Check for required packages
    if pip show openai &> /dev/null; then
        check_result 0 "openai package installed"
    else
        check_result 1 "openai package not installed"
        echo -e "   ${YELLOW}→${NC} Run: pip install -r requirements.txt"
    fi

    if pip show httpx &> /dev/null; then
        check_result 0 "httpx package installed"
    else
        check_result 1 "httpx package not installed"
        echo -e "   ${YELLOW}→${NC} Run: pip install -r requirements.txt"
    fi

    if pip show fastapi &> /dev/null; then
        check_result 0 "fastapi package installed"
    else
        check_result 1 "fastapi package not installed"
        echo -e "   ${YELLOW}→${NC} Run: pip install -r requirements.txt"
    fi
else
    check_result 1 "pip not found"
fi
echo ""

# 3. Check if service files exist
echo "3️⃣  Checking service files..."
[ -f "services/tts_service.py" ] && check_result 0 "TTS service exists" || check_result 1 "TTS service missing"
[ -f "services/stt_service.py" ] && check_result 0 "STT service exists" || check_result 1 "STT service missing"
[ -f "api/persona_router.py" ] && check_result 0 "Persona router exists" || check_result 1 "Persona router missing"
echo ""

# 4. Check frontend files
echo "4️⃣  Checking frontend files..."
[ -f "webapp/src/components/VoiceInterface.jsx" ] && check_result 0 "VoiceInterface component exists" || check_result 1 "VoiceInterface component missing"
[ -f "webapp/src/components/VoiceInterface.css" ] && check_result 0 "VoiceInterface styles exist" || check_result 1 "VoiceInterface styles missing"
[ -f "webapp/src/pages/PersonaBuilder.jsx" ] && check_result 0 "PersonaBuilder page exists" || check_result 1 "PersonaBuilder page missing"
echo ""

# 5. Check if MongoDB is running
echo "5️⃣  Checking MongoDB..."
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    if pgrep -x "mongod" > /dev/null; then
        check_result 0 "MongoDB is running"
    else
        check_result 1 "MongoDB is not running"
        echo -e "   ${YELLOW}→${NC} Start MongoDB: brew services start mongodb-community"
    fi
else
    echo -e "   ${YELLOW}⚠${NC}  MongoDB CLI not found (might be running in Docker)"
fi
echo ""

# 6. Test TTS service connectivity
echo "6️⃣  Checking TTS service..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://ai-tts.treppanliving.ae/health 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        check_result 0 "TTS service is reachable"
    else
        check_result 1 "TTS service returned HTTP $HTTP_CODE"
        echo -e "   ${YELLOW}→${NC} Service might be down or unreachable"
    fi
else
    echo -e "   ${YELLOW}⚠${NC}  curl not found, skipping TTS check"
fi
echo ""

# 7. Check Node.js and npm
echo "7️⃣  Checking Node.js environment..."
if command -v node &> /dev/null; then
    check_result 0 "Node.js is installed ($(node --version))"
else
    check_result 1 "Node.js is not installed"
fi

if command -v npm &> /dev/null; then
    check_result 0 "npm is installed ($(npm --version))"

    # Check if node_modules exists
    if [ -d "webapp/node_modules" ]; then
        check_result 0 "Frontend dependencies installed"
    else
        check_result 1 "Frontend dependencies not installed"
        echo -e "   ${YELLOW}→${NC} Run: cd webapp && npm install"
    fi
else
    check_result 1 "npm is not installed"
fi
echo ""

# Summary
echo "=============================================="
echo "📊 Summary:"
echo -e "   ${GREEN}Passed:${NC} $CHECKS_PASSED"
echo -e "   ${RED}Failed:${NC} $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All checks passed! You're ready to run the voice feature.${NC}"
    echo ""
    echo "🚀 Quick Start:"
    echo "   1. Backend:  uvicorn api.main:app --reload"
    echo "   2. Frontend: cd webapp && npm run dev"
    echo "   3. Open:     http://localhost:5173"
else
    echo -e "${YELLOW}⚠️  Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "📚 Documentation:"
    echo "   • Quick Start: VOICE_QUICKSTART.md"
    echo "   • Full Setup:  VOICE_PERSONA_SETUP.md"
fi
echo ""
