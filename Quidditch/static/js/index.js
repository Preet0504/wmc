const navbarEl = document.querySelector(".navbar");

const bottomContainerEl = document.querySelector(".bottom-container");

//console.log(bottomContainerEl.offsetTop) will give us the position at which the bottom container div starts. (basically height of the div)

window.addEventListener("scroll",()=>{ //activates the fucntion whenever we scroll.
    // console.log(scrollY)
    if(window.scrollY > bottomContainerEl.offsetTop - navbarEl.offsetHeight - 50){  //50 comes from the margin in text part in css
        navbarEl.classList.add("active");
    }
    else{
        navbarEl.classList.remove("active");
    }


});