// JavaScriptを使用して、client secretを取得する
const client_secret = document.getElementById('client_secret').value;

// JavaScriptを使用して、Stripeのインスタンスを作成する
const stripe = Stripe('pk_test_51OZnnyAiXkxmyRDeucSGGEKApynBgv8EeBdFF7IjOnxPtonAH31dmwqktZNmCM4wxs5UmbQXOzjoMQMTWPUql3A000ehqwxHwe');

// クレジットカード入力フォームで使用するElementsを設定し、上で取得したclient secretを渡す
const elements = stripe.elements({
    clientSecret:client_secret,
    appearance:{
        theme: 'stripe',
    },
});

const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// クレジットカード情報が送信された時の処理を記述する
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // confirmSetupを呼び出して支払い処理を完了させる
    const {error} = await stripe.confirmSetup({
        elements,
        confirmParams: {
            return_url: 'thanks/',
            }
           });

    if (error) {
        const messageContainer = document.querySelector('#error-message');
        messageContainer.textContent = error.message;
    } else {
        // none
    }
});

// 支払金額を取得
var paymentAmount = document.getElementById('paymentAmount').textContent;
// 隠しフィールドに設定
document.getElementById('paymentAmountInput').value = paymentAmount;