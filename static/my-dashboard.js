$(function() {
	const CLIENT_UUID = localStorage.getItem("client_uuid")
	const CLIENT_TOKEN = localStorage.getItem('client_token')

	if (CLIENT_TOKEN == undefined) {
		window.location.href = "/"
	}

	function showError(err) {
		alertify.error(err)
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
		loadAndDisplay($(this).attr("id").split('-')[0])
	})

	$("#newVault-btn").on('click', function() {
		// TODO: Let user custom the vault before creation

		$.ajax({
			url: "/kard-api/createVault",
			method: "POST",
			data: {
				"name": "KardWeb",
				"goal": 420
			},
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error);
				} else {
					loadAndDisplayVaults()
					alertify.success('Vault successfully created!');
				}
			}
		})
	})


	$(".rib.copyiban-btn").on('click', function() {
			var temp = $("<div>")
			$("body").prepend(temp)
			temp.attr("contenteditable", true)
   			temp.html($(".rib.iban").text()).select()
	    	temp.on("focus", function() {
	    		document.execCommand('selectAll',false,null)
	    	})
    		temp.focus()
			document.execCommand("copy")
			temp.remove()
	})

	$(".rib.download").on('click', function() {
		$.ajax({
			url: "/kard-api/downloadRib",
			method: "GET",
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error)
				} else {
					pdfFile = new Blob([result], {type: "application/pdf"})
					var a = document.createElement('a');
					var url = window.URL.createObjectURL(pdfFile);
					a.href = url;
					a.download = 'YourKardRIB.pdf';
					document.body.append(a);
					a.click();
					a.remove();
					window.URL.revokeObjectURL(url);
				}
			},
			error: function(result) {
				console.log(result)
			}	
		})
	})

	$(".toggleCheckbox.disabled").on('click', function(e) {
		e.preventDefault();
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

	function loadAndDisplay(thing) {
		$("#interchangeable-content > div.kard-box > div").each(function() {$(this).hide()})
		$("#interchangeable-content > div.kard-box > div.loader").show()

		if (thing == "limits") {loadAndDisplayLimits()}
		if (thing == "mastercard") {loadAndDisplayMastercard()}
		if (thing == "visa") {loadAndDisplayVisa()}
		if (thing == "rib") {loadAndDisplayRib()}
	}

	// Vaults
	function loadAndDisplayVaults() {
		$(".vault.a").each(function() {$(this).remove()})
		$(".vaults .loader").show()

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
							`<div class="vault a col" id="${c.id.slice(-10)}" style="background-color: ${c.color};">
								<!--
								<span class="position-absolute top-0 start-0 translate-middle p-2 bg-success rounded-circle">
									${Math.round((c.balance.value*100)/c.goal.value)}%
	    							<span class="visually-hidden">Completion percentage</span>
								</span>
								-->
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
					$(".vaults .loader").hide()
				}
			}
		})
	}

	// Limits
	function loadAndDisplayLimits() {
		$.ajax({
			url: "/kard-api/getLimits",
			method: "GET",
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error)
				} else {
					monthlyMaxPos = result.data.legalSpendingLimits.monthlyPos.value
					monthlyMaxAtm = result.data.legalSpendingLimits.monthlyAtm.value

					if (result.data.transactionLimits.length == 0) {
						$(".limits-subtitle").each(function() {$(this).text("Aucune limite fixée – Limites légales utilisées")})
					} else {
						parentSetMaxPos = result.data.transactionLimits.monthlyPos.value
						if (parentSetMaxPos > monthlyMaxPos) {
							monthlyMaxPos = parentSetMaxPos
						}
						parentSetMaxAtm = result.data.transactionLimits.monthlyAtm.value
						if (parentSetMaxAtm > monthlyMaxAtm) {
							monthlyMaxAtm = parentSetMaxAtm
						}
					}
					spentAgainstLimitPercentage = result.data.currentSpendings.monthlyPos.value*100/monthlyMaxPos
					cashoutAgainstLimitPercentage = result.data.currentSpendings.monthlyAtm.value*100/monthlyMaxAtm
					
					$(".limits-spent > .limits-progress").attr("title", `${result.data.currentSpendings.monthlyPos.value}€ dépensés sur ${monthlyMaxPos}€`)
					$(".limits-cashout > .limits-progress").attr("title", `${result.data.currentSpendings.monthlyAtm.value}€ retirés sur ${monthlyMaxAtm}€`)

					$(".limits-progress").append(
						`<style>
							@keyframes loadPaiement {
								0% {width: 0;}
								100% {width: ${spentAgainstLimitPercentage}%;}
							}
							@keyframes loadCashout {
								0% {width: 0;}
								100% {width: ${cashoutAgainstLimitPercentage}%;}
							}
						</style>`
					)

					authorizations = result.data.transactionAuthorizations
					for (let i=0; i<authorizations.length;i++) {
						auth = authorizations[i]
						if (auth.authorizationType == "ATM") {
							check = $(".check.allowcashout")
							if (auth.isAuthorized == true) {
								check.css("color", "#0F0")
								check.html('<i class="fa-duotone fa-check"></i>')
							} else {
								check.css("color", "#F00")
								check.html('<i class="fa-regular fa-circle-xmark"></i>')
							}
						}
						if (auth.authorizationType == "ONLINE") {
							check = $(".check.onlinepay")
							if (auth.isAuthorized == true) {
								check.css("color", "#0F0")
								check.html('<i class="fa-duotone fa-check"></i>')
							} else {
								check.css("color", "#F00")
								check.html('<i class="fa-regular fa-circle-xmark"></i>')
							}
						}
						if (auth.authorizationType == "INTERNATIONAL") {
							check = $(".check.international")
							if (auth.isAuthorized == true) {
								check.css("color", "#0F0")
								check.html('<i class="fa-duotone fa-check"></i>')
							} else {
								check.css("color", "#F00")
								check.html('<i class="fa-regular fa-circle-xmark"></i>')
							}
						}
					}


					// Hide & Display
					$("#interchangeable-content > div.kard-box > div").each(function() {$(this).hide()})
					$("#limits").show()
				}
			}
		})
	}
	// Kard MasterCard
	function loadAndDisplayMastercard() {
		$.ajax({
			url: "/kard-api/getMastercardInfos",
			method: "GET",
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error)
				} else {
					$("#mastercard > div > .card-number").text(result.data.visibleNumber)
					$("#mastercard > div > .card-holder").text(result.data.name)
					$("#mastercard").append(`<input type="hidden" value="${result.data.id}">`)

					// Hide & Display
					$("#interchangeable-content > div.kard-box > div").each(function() {$(this).hide()})
					$("#mastercard").show()
				}
			}
		})
	}
	// Kard Visa
	function loadAndDisplayVisa() {
		$.ajax({
			url: "/kard-api/getVisaInfos",
			method: "GET",
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error)
				} else {
					$("#visa > div > .card-number").text(result.data.card_number)
					$("#visa > div > .card-expi").text(result.data.expiration_date)
					$("#visa > div > .card-cvv").text(result.data.cvv)
					$("#visa > div > .card-holder").text(result.data.card_holder)

					$("#visa").append(`<input type="hidden" value="${result.data.id}">`)
					
					// Hide & Display
					$("#interchangeable-content > div.kard-box > div").each(function() {$(this).hide()})
					$("#visa").show()
				}
			}
		})
	}
	// Kard RIB
	function loadAndDisplayRib() {
		$.ajax({
			url: "/kard-api/getRibInfos",
			method: "GET",
			beforeSend: function(request) {
				request.setRequestHeader("k-device-uuid", CLIENT_UUID)
				request.setRequestHeader("k-authorization-token", CLIENT_TOKEN)
			},
			success: function(result) {
				if (result.status == -1) {
					showError(result.error)
				} else {
					console.log(result.data)
					$("#rib").append(`<input type="hidden" value="${result.data.id}">`)
					$(".rib.iban").text(result.data.iban)
					$(".rib.bic").text(result.data.bic)
					$(".rib.user").text(result.data.user.firstName + ' ' + result.data.user.lastName)
					
					// Hide & Display
					$("#interchangeable-content > div.kard-box > div").each(function() {$(this).hide()})
					$("#rib").show()
				}
			}
		})
	}


	// Transactions (Load 10, then lazy-load)
	$.ajax({
		url: "/kard-api/getTransactions",
		method: "GET",
		data: {"maxi": "10"},
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

	loadAndDisplayVaults()
	loadAndDisplayLimits()


})