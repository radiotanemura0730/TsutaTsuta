var stripe = Stripe("{{ STRIPE_API_PUBLIC_KEY }}");
var elements = stripe.elements();
var cardElement = elements.create('card');
cardElement.mount('#card-element');
var cardholderName = document.getElementById('cardholder-name');
var cardButton = document.getElementById('card-button');
var clientSecret = "{{ client_secret }}";
cardButton.addEventListener('click', function (ev) {
    stripe.confirmCardSetup(
    clientSecret,
    {
        payment_method: {
        card: cardElement,
        },
    }
    ).then(function (result) {
    if (result.error) {
        // Display error.message in your UI.
        toast(result.error.message, 'error');
    } else {
        toast("クレジットカードが登録されました。", 'success');
        window.location.reload();
        // The setup has succeeded. Display a success message.
    }
    });
});    