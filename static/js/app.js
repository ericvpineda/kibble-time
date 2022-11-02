const clouds = document.getElementById('clouds')
const sun = document.getElementById('sun')
const mountains = document.getElementById('mountains')
const text = document.getElementById('text')
const backyard = document.getElementById('backyard')
const btn = document.getElementById('explore_btn')
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
    const value = window.scrollY;
    clouds.style.left = value * 0.25 + "px"; 
    sun.style.top = value * 1.05 + "px"; 
    mountains.style.top = value * 0.5 + "px"; 
    text.style.marginRight = value * 2 + "px"; 
    btn.style.marginTop = value * 1.5 + "px";
    header.style.top = value * 0.5 + "px";
})