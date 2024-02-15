function applyPoint() {
    const pointInput = document.getElementById('pointInput');
    const usePointSpan = document.getElementById('use_point');

    const inputValue = parseInt(pointInput.value);
    usePointSpan.textContent = inputValue; // 使用ポイントを表示

    const price = parseInt(document.getElementById('price').textContent); // 商品代金を取得
    const usePoint = parseInt(document.getElementById('use_point').textContent); // 所有ポイントを取得

    const paymentAmount = document.getElementById('paymentAmount');
    const amount = price - usePoint; // 使用ポイントを計算
    paymentAmount.textContent = amount; // 支払い金額を表示

    // フォームのamountにも設定する
    document.getElementById('paymentAmountInput').value = amount;
}