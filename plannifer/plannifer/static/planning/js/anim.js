let title = document.getElementById('test');

title.addEventListener('click', function(event) {
    event.stopPropagation();
    title.textContent = "OMG";
    title.style.color = "red";
    title.style.backgroundColor = "blue";
    title.style.fontWeight = "bold";
});

title.addEventListener('mouseover', function(event) {
    event.stopPropagation();
    title.textContent = "OMG";
    title.style.color = "red";
    title.style.backgroundColor = "blue";
    title.style.fontWeight = "bold";
});

title.addEventListener('mouseout', function(event) {
    event.stopPropagation();
    title.textContent = "OMG";
    title.style.color = "blue";
    title.style.backgroundColor = "red";
    title.style.fontWeight = "light";
});