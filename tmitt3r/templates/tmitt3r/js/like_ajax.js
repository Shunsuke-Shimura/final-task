'use strict';
function tm33tLikeAjax(obj) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Likeのハートのスタイルを切り替える
            toggleHeartStyle(obj);
        }
    }
    // POSTするデータの作成
    let tm33tPk = obj.dataset.tm33tPk;
    let nextState = obj.dataset.nextState;
    let data = `like=${nextState}&pk=${tm33tPk}`;
    const URL = '/tm33t/like/';
    // nextStateを切り替える
    if (nextState === 'like') {
        obj.dataset.nextState = 'unlike';
    } else {
        obj.dataset.nextState = 'like';
    }
    xhr.open('POST', URL, true);
    xhr.send(data);
}
function toggleTm33tLike(obj) {
    if (obj.nextState === 'like') {
        // unlike
        obj.classList.remove('like');
        obj.classList.remove('fas');
        obj.classList.add('far');
    } else {
        // like
        obj.classList.add('like');
        obj.classList.remove('far');
        obj.classList.add('fas');
    }
}
