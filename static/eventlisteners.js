// for bird page

<button id='faveOnOff' class='faveText'>Favorite</button>

<script>
  "use strict";

let faveButton = document.querySelector('.faveText');

function faveUnfave(evt) {

  if (faveButton.innerHTML === 'Favorite') {
    faveButton.innerHTML = 'Unfavorite';
  }
  else: {
    faveButton.innerHTML = 'Favorite';
  }
}

faveButton.addEventListener('click', faveUnfave);

</script>




<script>




</script>