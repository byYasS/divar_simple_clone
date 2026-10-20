/*
 * Shows dates as Persian (Jalali) dates in the browser. No backend code is needed.
 * The browser's built-in Intl API already knows the Persian calendar.
 *
 * In a template, write the date as a <time> element:
 *
 *   <time class="js-jalali" datetime="{{ obj.created_at|date:'c' }}" data-format="long">
 *       {{ obj.created_at|date:"Y/m/d" }}
 *   </time>
 *
 * data-format:  short | long (default) | datetime | long_datetime
 *   short          ۱۴۰۵/۰۷/۲۷
 *   long           ۲۷ مهر ۱۴۰۵
 *   datetime       ۱۴۰۵/۰۷/۲۷ - ۱۴:۳۵
 *   long_datetime  ۲۷ مهر ۱۴۰۵، ساعت ۱۴:۳۵
 *
 * The text inside the tag is only a fallback (shown if JavaScript is off).
 */
(function () {
    'use strict';

    // Persian calendar + Persian digits
    var LOCALE = 'fa-IR-u-ca-persian-nu-arabext';

    // Always show Tehran time. Set to undefined to use each visitor's own time zone.
    var TIME_ZONE = 'Asia/Tehran';

    var DATE_SHORT = {year: 'numeric', month: '2-digit', day: '2-digit'};
    var DATE_LONG = {year: 'numeric', month: 'long', day: 'numeric'};
    var TIME = {hour: '2-digit', minute: '2-digit', hourCycle: 'h23'};

    var STYLES = {
        short:         {date: DATE_SHORT},
        long:          {date: DATE_LONG},
        datetime:      {date: DATE_SHORT, time: TIME, joiner: ' - '},
        long_datetime: {date: DATE_LONG,  time: TIME, joiner: '، ساعت '}
    };

    var cache = {};

    function makeFormatter(options) {
        var opts = {};
        for (var key in options) { opts[key] = options[key]; }
        if (TIME_ZONE) { opts.timeZone = TIME_ZONE; }
        return new Intl.DateTimeFormat(LOCALE, opts);
    }

    function getFormatters(style) {
        if (!STYLES[style]) { style = 'long'; }
        if (!cache[style]) {
            cache[style] = {
                date: makeFormatter(STYLES[style].date),
                time: STYLES[style].time ? makeFormatter(STYLES[style].time) : null,
                joiner: STYLES[style].joiner || ''
            };
        }
        return cache[style];
    }

    // Returns the formatted text, or null if the value is not a valid date.
    function format(iso, style) {
        var date = new Date(iso);
        if (isNaN(date.getTime())) { return null; }

        var f = getFormatters(style || 'long');
        var text = f.date.format(date);
        if (f.time) { text += f.joiner + f.time.format(date); }
        return text;
    }

    function renderElement(el) {
        var text = format(el.getAttribute('datetime'), el.getAttribute('data-format'));
        if (text) { el.textContent = text; }
    }

    // Convert every <time class="js-jalali"> inside `root` (default: the whole page).
    function render(root) {
        root = root || document;
        if (root.matches && root.matches('time.js-jalali')) { renderElement(root); }
        if (!root.querySelectorAll) { return; }
        var items = root.querySelectorAll('time.js-jalali');
        for (var i = 0; i < items.length; i++) { renderElement(items[i]); }
    }

    // initial page
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { render(); });
    } else {
        render();
    }

    // content added later by htmx (e.g. the infinite scroll of the listings)
    document.addEventListener('htmx:load', function (e) { render(e.target); });

    // available for other scripts too: JalaliDates.format(iso, 'long')
    window.JalaliDates = {render: render, format: format};
})();
