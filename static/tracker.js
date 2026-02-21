/**
 * SellSmart Engagement Tracker
 * 
 * Client-side telemetry for tracking buyer interactions with microsites.
 * Captures: page views, section dwell time, scroll depth, CTA clicks, session end.
 * Events are batched and sent to the backend API.
 */
(function () {
    'use strict';

    // Configuration
    const BATCH_INTERVAL_MS = 5000; // Send events every 5 seconds
    const DWELL_THRESHOLD_MS = 1000; // Minimum dwell time to record (1 second)
    const API_BASE = window.location.origin;

    // Extract tracking metadata from page
    const trackingId = document.querySelector('meta[name="tracking-id"]')?.content || '';
    const personaId = document.querySelector('meta[name="persona-id"]')?.content || '';

    if (!trackingId) {
        console.warn('[SellSmart Tracker] No tracking-id found. Tracking disabled.');
        return;
    }

    // Session state
    const sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
    const eventQueue = [];
    let maxScrollDepth = 0;
    const sectionStartTimes = {}; // section name → timestamp when it became visible
    const sectionDwellTimes = {}; // section name → accumulated dwell in seconds

    // ─── Event Helpers ───────────────────────────────────

    function queueEvent(eventType, payload) {
        eventQueue.push({
            event_type: eventType,
            payload: payload || {},
            timestamp: new Date().toISOString(),
        });
    }

    function flushEvents() {
        if (eventQueue.length === 0) return;

        const batch = eventQueue.splice(0, eventQueue.length);

        fetch(API_BASE + '/api/v1/engagement/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tracking_id: trackingId,
                session_id: sessionId,
                events: batch,
            }),
            keepalive: true, // Ensure events are sent even on page close
        }).catch(function (err) {
            console.warn('[SellSmart Tracker] Failed to send events:', err);
            // Re-queue failed events
            eventQueue.push.apply(eventQueue, batch);
        });
    }

    // ─── Page View ───────────────────────────────────────

    queueEvent('page_view', {
        url: window.location.href,
        referrer: document.referrer,
        user_agent: navigator.userAgent,
        screen_width: screen.width,
        screen_height: screen.height,
    });

    // ─── Scroll Depth ────────────────────────────────────

    function getScrollDepth() {
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        );
        var winHeight = window.innerHeight;
        return Math.min(Math.round(((scrollTop + winHeight) / docHeight) * 100), 100);
    }

    var scrollThrottleTimer = null;
    window.addEventListener('scroll', function () {
        if (scrollThrottleTimer) return;
        scrollThrottleTimer = setTimeout(function () {
            scrollThrottleTimer = null;
            var depth = getScrollDepth();
            if (depth > maxScrollDepth) {
                maxScrollDepth = depth;
                // Record at 25%, 50%, 75%, 100% milestones
                if (depth >= 25 && depth < 50) {
                    queueEvent('scroll_depth', { depth_percent: 25 });
                } else if (depth >= 50 && depth < 75) {
                    queueEvent('scroll_depth', { depth_percent: 50 });
                } else if (depth >= 75 && depth < 100) {
                    queueEvent('scroll_depth', { depth_percent: 75 });
                } else if (depth >= 100) {
                    queueEvent('scroll_depth', { depth_percent: 100 });
                }
            }
        }, 200);
    });

    // ─── Section Dwell Time (IntersectionObserver) ───────

    var sections = document.querySelectorAll('[data-section]');

    if ('IntersectionObserver' in window && sections.length > 0) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var sectionName = entry.target.getAttribute('data-section');
                if (!sectionName) return;

                if (entry.isIntersecting) {
                    // Section entered viewport
                    sectionStartTimes[sectionName] = Date.now();
                } else {
                    // Section left viewport — calculate dwell
                    if (sectionStartTimes[sectionName]) {
                        var elapsed = (Date.now() - sectionStartTimes[sectionName]) / 1000;
                        if (elapsed * 1000 >= DWELL_THRESHOLD_MS) {
                            sectionDwellTimes[sectionName] = (sectionDwellTimes[sectionName] || 0) + elapsed;
                            queueEvent('section_focus', {
                                section: sectionName,
                                dwell_seconds: Math.round(elapsed * 10) / 10,
                                total_dwell: Math.round((sectionDwellTimes[sectionName]) * 10) / 10,
                            });
                        }
                        delete sectionStartTimes[sectionName];
                    }
                }
            });
        }, { threshold: 0.5 }); // 50% of section must be visible

        sections.forEach(function (section) {
            observer.observe(section);
        });
    }

    // ─── CTA Click Tracking ─────────────────────────────

    document.addEventListener('click', function (e) {
        var target = e.target.closest('a[id^="cta-"], button[id^="cta-"]');
        if (target) {
            queueEvent('cta_click', {
                cta_id: target.id,
                cta_text: target.textContent.trim().substring(0, 100),
                cta_href: target.href || '',
            });
            // Flush immediately on CTA click (high-value event)
            flushEvents();
        }
    });

    // ─── Session End ────────────────────────────────────

    window.addEventListener('beforeunload', function () {
        // Flush any remaining section dwell times
        Object.keys(sectionStartTimes).forEach(function (sectionName) {
            var elapsed = (Date.now() - sectionStartTimes[sectionName]) / 1000;
            if (elapsed * 1000 >= DWELL_THRESHOLD_MS) {
                sectionDwellTimes[sectionName] = (sectionDwellTimes[sectionName] || 0) + elapsed;
                queueEvent('section_focus', {
                    section: sectionName,
                    dwell_seconds: Math.round(elapsed * 10) / 10,
                    total_dwell: Math.round((sectionDwellTimes[sectionName]) * 10) / 10,
                });
            }
        });

        queueEvent('session_end', {
            max_scroll_depth: maxScrollDepth,
            total_dwell_times: Object.assign({}, sectionDwellTimes),
            session_duration_seconds: Math.round((Date.now() - performance.timing.navigationStart) / 1000),
        });

        flushEvents();
    });

    // ─── Periodic Flush ─────────────────────────────────

    setInterval(flushEvents, BATCH_INTERVAL_MS);

    console.log('[SellSmart Tracker] Initialized. Tracking ID:', trackingId, 'Session:', sessionId);
})();
