// JavaScriptを使用して、client secretを取得する
const client_secret = document.getElementById('client_secret').value;

// JavaScriptを使用して、Stripeのインスタンスを作成する
// 本番環境では本番用の公開可能鍵を用意する
const stripe = Stripe('pk_test_51OZnnyAiXkxmyRDeucSGGEKApynBgv8EeBdFF7IjOnxPtonAH31dmwqktZNmCM4wxs5UmbQXOzjoMQMTWPUql3A000ehqwxHwe');

// クレジットカード入力フォームで使用するElementsを設定し、上で取得したclient secretを渡す
const elements = stripe.elements({
    clientSecret:client_secret,
    appearance:{
        theme: 'stripe',
    },
});

// Payment Elementを作成し、既存のDOM要素から生成したDOM要素に置き換える
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// id=payment-formの要素を取得する
const form = document.getElementById('payment-form');

// クレジットカード情報が送信された時の処理を記述する
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // confirmSetupを呼び出して支払い処理を完了させる
    const {error} = await stripe.confirmSetup({
        elements,
        confirmParams: {
            return_url: '/thanks', /* 支払い完了後に呼び出すURL（ここでは/thanks） */
            }
           });

    if (error) {
        const messageContainer = document.querySelector('#error-message');
        messageContainer.textContent = error.message;
    } 
});