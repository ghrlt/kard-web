$(function() {
	const CLIENT_UUID = localStorage.getItem("client_uuid")
	const CLIENT_TOKEN = localStorage.getItem('client_token')

	if (CLIENT_TOKEN == undefined) {
		window.location.href = "/"
	}

	function showError(err) {
		alert(err)
	}

	$.ajax({
		url: "/kard-api/fetch/firstname",
		method: "GET",
		beforeSend: function(request) {
			request.setRequestHeader("k-device-uuid", CLIENT_UUID)
			request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
		},
		success: function(result) {
			if (result.status == -1) {
				showError(result.error);
			} else {
				$("#firstname").text(result.data.fetched)
			}
		}
	})



})