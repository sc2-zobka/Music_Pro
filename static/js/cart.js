var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
		if (user == 'AnonymousUser'){
			console.log('User is not authenticated')
			
		}else{
			updateUserOrder(productId, action)
		}



	})
}

function updateUserOrder(productId, action) {
    console.log("User is authenticated, sending data...")

	//Ajax request working but not changing 
	//product quantity and cart icon item
	$.ajax({
		type: 'POST',
		url: '/update_item/',
		headers: {
			'Content-Type':'application/json',
			'X-CSRFToken': csrftoken,
		},
		data: JSON.stringify({'productId':productId, 'action':action})
	})
	.then((response) => {
		return response.json()
	 })
	 .then((data) => {
		 location.reload()
	 })

}
