document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.checkbox-round');
    const displayTexts = document.querySelectorAll('.displayText');
    console.log("test")
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('click', function() {
            console.log(this);
            if (this.checked) {
                displayTexts[index].style.display = 'block'; // テキストを表示
            } else {
                displayTexts[index].style.display = 'none'; // テキストを非表示
            }
        });
    });
});