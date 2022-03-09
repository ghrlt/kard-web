$(function() {
	if (localStorage.getItem('client_token') != undefined) {
		window.location.href = "/dashboard"
	}


	function clearErrorMsg() {
		$("#tel-error").text("")
		$("#otp-error").text("")
		$("#pin-error").text("")
	}
	clearErrorMsg()


	/* Generate UUID for KardApi */
	function uuidv4() {
		return ([1e7]+-1e5+-4e4+-1e11).replace(
					/[018]/g,
					c => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
	)}

	if (localStorage.getItem("client_uuid") == undefined) {
		localStorage.setItem("client_uuid", uuidv4())
	}
	const CLIENT_UUID = localStorage.getItem("client_uuid")


	$("#tel-btn").on('click', function() {
		clearErrorMsg()

		$.ajax({
			url: "/login/request-otp",
			method: "POST",
			data: {
				"tel": $("#KardTel").val()
			},
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID);
			},
			success: function(result) {
				if (result.status == -1) {
					$("#tel-error").text(result.error)
				} else {
					$("#tel-btn").hide()
					$("#tel > .kard-input-text, #tel > div > .kard-input").addClass("-reduced")

					if (result.data.pin == true) {
						$("#pin, #pin-btn").show()
					} else {
						$("#otp-btn, #otp").show()
					}
				}
			}

		})
	})
	$("#otp-btn").on('click', function() {
		clearErrorMsg()

		$.ajax({
			url: "/login/confirm-otp",
			method: "POST",
			data: {
				"tel": $("#KardTel").val(),
				"otp": $("#KardOtp").val()
			},
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID);
			},
			success: function(result) {
				if (result.status == -1) {
					$("#otp-error").text(result.error)
				} else {
					$("#otp").removeClass("pt-5")
					$("#otp > .kard-input-text, #otp > div > .kard-input").addClass("-reduced")
					$("#otp-btn").hide()
					$("#pin, #pin-btn").show()
				}
			}

		})
	})
	$("#pin-btn").on('click', function() {
		clearErrorMsg()

		$.ajax({
			url: "/login/confirm-pin",
			method: "POST",
			data: {
				"tel": $("#KardTel").val(),
				"pin": $("#KardPin").val()
			},
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID);
			},
			success: function(result) {
				if (result.status == -1) {
					$("#pin-error").text(result.error)
				} else {
					localStorage.setItem('client_token', result.data.token)
					window.location.href = "/dashboard"
				}
			}

		})
	})
})