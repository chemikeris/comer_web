window.onscroll = function() {showScrollButton();}
function showScrollButton() {
    var button = document.getElementById('top_button');
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        button.style.display = 'block';
    }
    else {
        button.style.display = 'none';
    }
}
function goToTop() {
    window.scrollTo({top: 0, behavior: 'smooth'});
}
