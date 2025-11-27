// Sử dụng event delegation để tránh việc gán nhiều event listener
// và đảm bảo các nút được thêm sau cũng hoạt động.
document.addEventListener('click', function(e) {
    // Chỉ thực thi nếu phần tử được click có class 'update-cart-btn'
    if (e.target && e.target.classList.contains('update-cart-btn')) {
        e.preventDefault(); // Ngăn hành vi mặc định của nút

        const productId = e.target.dataset.product;
        const action = e.target.dataset.action;

        console.log('productId:', productId, 'action:', action);
        console.log('USER:', user);

        if (user === 'AnonymousUser' || user === '') {
            console.log('User is not logged in');
            // Có thể chuyển hướng đến trang đăng nhập hoặc hiển thị thông báo
            // window.location.href = '/login/'; 
        } else {
            updateUserOrder(productId, action);
        }
    }
});

function updateUserOrder(productId, action) {
    console.log('User is logged in, sending data...');
    const url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
    .then((response) => {
        // Kiểm tra nếu response không ok (vd: lỗi 500, 404)
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then((data) => {
        console.log('data:', data);
        
        // Cập nhật số lượng trên icon giỏ hàng
        const cartTotalElement = document.getElementById('cart-total');
        if (cartTotalElement) {
            cartTotalElement.innerText = data.total_items;
        }

        // Nếu bạn đang ở trang giỏ hàng (cart.html), bạn có thể muốn reload 
        // để cập nhật danh sách sản phẩm và tổng tiền.
        // Nếu không phải trang giỏ hàng, việc chỉ cập nhật số lượng là đủ.
        if (window.location.pathname === "/cart/") {
            location.reload();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        // Có thể hiển thị thông báo lỗi cho người dùng ở đây
    });
}