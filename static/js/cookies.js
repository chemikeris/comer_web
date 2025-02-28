function reject_cookielaw() {
    Cookielaw.createCookie('cookielaw_accepted', 0, days='', secure=true);
    Cookielaw.hideCookielawBanner();
}
