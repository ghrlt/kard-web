$(function() {
	const CLIENT_UUID = localStorage.getItem("client_uuid")
	const CLIENT_TOKEN = localStorage.getItem('client_token')

	if (CLIENT_TOKEN == undefined) {
		window.location.href = "/"
	}

	function showError(err) {
		alert(err)
	}

	$("#selftransactions-btn").on('click', function() {
		$("#selftransactions-btn > span").addClass("underlined")
		$("#friendstransactions-btn > span").removeClass("underlined")

		$("#selftransactions-list").show()
		$("#friendstransactions-list").hide()
	})
	$("#friendstransactions-btn").on('click', function() {
		$("#friendstransactions-btn > span").addClass("underlined")
		$("#selftransactions-btn > span").removeClass("underlined")

		$("#selftransactions-list").hide()
		$("#friendstransactions-list").show()
	})

	$(".icon-shortcut").on('click', function() {
		$("#tran")
	})

	// Firstname
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
	// Balance
	$.ajax({
		url: "/kard-api/fetch/balance",
		method: "GET",
		beforeSend: function(request) {
			request.setRequestHeader("k-device-uuid", CLIENT_UUID)
			request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
		},
		success: function(result) {
			if (result.status == -1) {
				showError(result.error);
			} else {
				$("#balance").text(result.data.fetched + "€")
			}
		}
	})
	// Vaults
	$.ajax({
		url: "/kard-api/getVaults",
		method: "GET",
		beforeSend: function(request) {
			request.setRequestHeader("k-device-uuid", CLIENT_UUID)
			request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
		},
		success: function(result) {
			if (result.status == -1) {
				showError(result.error);
			} else {
				for (let i=0;i<result.data.vaults.length;i++) {
					c = result.data.vaults[i]

					$(".vaults").prepend(
						`<div class="vault col" id="${c.id.slice(-10)}" style="background-color: ${c.color};">
							<div class="-centered">
								<span class="vault-emote">${c.emoji.unicode}</span>
							</div>
							<div class="-centered pt-2">
								<span class="kard-title -black">${c.name}</span>
							</div>
							<div class="-centered">
								<span class="kard-text">
									<span class="vault-in">${c.balance.value}€</span>
									<span class="vault-balance-separator"> / </span>
									<span class="vault-goal">${c.goal.value}€</span>
								</span>
							</div>
						</div>`
					)
				}
			}
		}
	})
	// Transactions (Load 10, then lazy-load)
	$.ajax({
		url: "/kard-api/getTransactions",
		method: "GET",
		data: {"args": {"maxi": "10"}},
		beforeSend: function(request) {
			request.setRequestHeader("k-device-uuid", CLIENT_UUID)
			request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
		},
		success: function(result) {
			if (result.status == -1) {
				showError(result.error);
			} else {
				for (let i=0; i<result.data.length;i++) {
					t = result.data[i]

					$("#selftransactions-list").append(
						`
						<div class="kard-transaction transaction-status-${t.status.toLowerCase()} transaction-type-${t.__typename}"
								id="${t.id.slice(-10)}">
							<div class="row row-no-gutter w-100">
								<div class="col col-1 kard-transaction-icon" style="background-image: url(${t.category.image.url});"></div>
								<div class="col col-7" style="display: flex; align-items: center;">
									<div class="kard-transaction-text row">
										<div class="col col-12">
											<span class="kard-transaction-title"
												title="${t.title}">
													${t.title}
											</span>
										</div>
										<div class="col col-12">
											<span class="kard-transaction-subtitle">${t.category.name}</span>
										</div>
									</div>
								</div>
								<div class="col col-4 kard-transaction-amount">
									<div class="kard-transaction-text">
										<span>${t.amount.value}</span>
										<span>€</span>
									</div>
								</div>
							</div>
						</div>

						`
					)
				}
			}
		}

	})



})