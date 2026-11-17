/* HTTP to HTTPS fallback for yushufang.org only.
   GitHub Pages "Enforce HTTPS" is a repository setting and is the redirect that should be turned on.
   This runs only if a request still arrives over http on the production host. It does nothing on https or on any other host. */
(() => { if (location.protocol === 'http:' && ['yushufang.org','www.yushufang.org'].includes(location.hostname)) location.replace('https://yushufang.org' + location.pathname + location.search + location.hash); })();
