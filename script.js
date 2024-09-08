function setActive(page){
  try {
    if (document.querySelector('header').innerHTML.includes('active')){
      var activepage = document.querySelector('header.topnav a.active');
      activepage.classList.remove('active');
    }
  } catch (error){}
  
  if (page == '' || page == '/'){
    document.querySelector('header.topnav a').classList.add('active');
  } else {
    document.querySelector('header.topnav a[href="#' + page + '"]').classList.add('active');
  }
}

if (window.location.href.includes('#')){
  setActive(window.location.hash.replace('#', ''));
} else {
  setActive('home');
}

function sendIssue(title, body = '', assignees = 'samuellouf'){
  var link = `https://github.com/samuellouf/PyBrowser/issues/new?labels=bug&body=${body}&title=${title}&assignees=${assignees}`;
  var a = document.createElement('a');
  a.href = link;
  a.target = '_blank'
  a.click();
}

let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "flex";  
  dots[slideIndex-1].className += " active";
}