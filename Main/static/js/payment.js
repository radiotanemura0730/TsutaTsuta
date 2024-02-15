var pointInput = document.getElementById('pointInput');

pointInput.addEventLisner('submit',function(){
    var newPoints = parseInt(pointInput.value);

    document.getElementById('use_point').innerText = newPoints;
})