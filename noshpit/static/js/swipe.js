document.addEventListener("DOMContentLoaded", function(event) {
    var el = document.getElementById("food-photo");

    el.addEventListener('touchstart', handleTouchStart, false);
    el.addEventListener('touchmove', handleTouchMove, false);

    var xDown = null;
    var yDown = null;
});

function handleTouchStart(evt) {
    xDown = evt.touches[0].clientX;
    yDown = evt.touches[0].clientY;
};

function handleTouchMove(evt) {
    if ( ! xDown || ! yDown ) {
        return;
    }

    var xUp = evt.touches[0].clientX;
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;

    if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
        if ( xDiff > 0 ) {
            /* left swipe */
            window.location.href = '/photos';
        } else {
            /* right swipe */
            window.location.href = '/yes';
        }
    } else {
        if ( yDiff > 0 ) {
            /* up swipe */
        } else {
            /* down swipe */
        }
    }
    /* reset values */
    xDown = null;
    yDown = null;
};
