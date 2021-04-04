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
    let postState = '';
    const URL = '/tm33t/like/';
    // stateを切り替える
    if (obj.dataset.state === 'like') {
        postState = 'unlike';
    } else {
        postState = 'like';
    }
    let data = `like=${postState}&pk=${tm33tPk}`;
    xhr.open('POST', URL, true);
    xhr.send(data);
}

function toggleTm33tLike(obj) {
    if (obj.dataset.state === 'like') {
        obj.dataset.state = 'unlike';
        obj.classList.remove('like');
        obj.classList.remove('fas');
        obj.classList.add('far');

    } else {
        obj.dataset.state === 'unlike';
        obj.classList.add('like');
        obj.classList.remove('far');
        obj.classList.add('fas');
    }
}
