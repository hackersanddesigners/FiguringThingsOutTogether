this.ready = new Promise(function ($) {
	document.addEventListener("DOMContentLoaded", $, { once: true });
});


class MM_Handler extends Paged.Handler {
	t0 = 0; t1 = 0;
	constructor(chunker, polisher, caller) {
		super(chunker, polisher, caller);
		this.chunker = chunker;
		this.polisher = polisher;
		this.caller = caller;
	}

	beforeParsed(content) {
		insertUIStyle();
	}

	afterPageLayout(pageElement, page, breakTokenage) {
		// return this.alignImagesToBaseline(pageElement, 12);

		const el = page.element.querySelector('.pagedjs_footnote_inner_content .footnote[data-split-from]');
		if( el ){
			el.removeAttribute('data-split-from')
			el.classList.add('continued-footnote');
			el.style.counterIncrement = 'revert';
		}
	}

	afterPreview(pages) {
		this.t0 = performance.now();
		if (typeof renderSketch === 'function') {
			this.renderBackground(pages, 0);
		} else {
			removeLoadingMessage();
		}
	}

	renderBackground(pages, idx) {
		let page = pages[idx];
		if (typeof renderSketch === 'function') {
			renderSketch(page, idx + 1);
		}
		if (idx < pages.length - 1) {
			idx++;
			setTimeout(() => { this.renderBackground(pages, idx) }, 10);
		} else {
			this.t1 = performance.now();
			console.log("Rendering backgrounds for " + pages.length + " pages took " + (this.t1 - this.t0) + " milliseconds.");
		}
	}

	alignImagesToBaseline(elem, gridSize) {
		const imgs = elem.querySelectorAll('img:not(.full)');
		let rythm = gridSize / 72 * 96; // convert pt to px
		imgs.forEach((img, i) => {
			// img.parentNode.parentNode.classList.add("image-container") // add class to p remove margins
			let oldH = img.clientHeight;
			let newH = Math.floor(oldH / rythm) * rythm;
			img.style.height = newH + "px";
			console.log(`resized image from ${oldH} to ${newH} (${img.src})`);
		});
	};
}

ready.then(async function () {

	let flowText = document.querySelector("#source");

	let t0 = performance.now();
	Paged.registerHandlers(MM_Handler);
	let paged = new Paged.Previewer();

	paged.preview(flowText.content).then((flow) => {
		let t1 = performance.now();
		console.log("Rendering Pagedjs " + flow.total + " pages took " + (t1 - t0) + " milliseconds.");
	});


	let resizer = () => {
		let pages = document.querySelector(".pagedjs_pages");

		if (pages) {
			let scale = (window.innerWidth * 0.9) / pages.offsetWidth;
			if (scale < 1) {
				pages.style.transform = `scale(${scale}) translate(${window.innerWidth / 2 - (pages.offsetWidth * scale) / 2
					}px, 0)`;
			} else {
				pages.style.transform = "none";
			}
		}
	};
	resizer();

	window.addEventListener("resize", resizer, false);

	paged.on("rendering", () => {
		resizer();
	});

	/* initialize ui */
	ui();
});


let ui = () => {
	let queryParams = new URLSearchParams(window.location.search);
	// let checks = ['grid', 'hide_foreground', 'hide_background'];
	let checks = document.querySelectorAll('.print-ui-element input[type=checkbox]');
	checks.forEach(function (check) {
		check.addEventListener('change', (event) => {
			value = check.checked == 1 ? 1 : 0;
			let name = check.id;
			queryParams.set(name, value);
			history.replaceState(null, null, "?" + queryParams.toString());
			if (value == 0) {
				document.body.classList.remove(name);
			} else {
				document.body.classList.add(name);
			}
		});
	});
	// for(let i = 0; i < checks.length; i++ ){
	// 	let name = checks[i];
	// 	const el = document.getElementById(name);
	// 	el.addEventListener('change', (event) => {
	// 		value = el.checked == 1 ? 1 : 0;
	// 		queryParams.set(name, value);
	// 		history.replaceState(null, null, "?"+queryParams.toString());
	// 		if( value == 0 ) {
	// 			document.body.classList.remove(name);
	// 		} else {
	// 			document.body.classList.add(name);
	// 		}
	// 	});
	// }
}

let insertUIStyle = () => {
	const style = document.createElement('style');
	style.innerHTML = `
		@media only print {
      .print-ui {
        display: none !important	;
      }
		}
		.print-ui {
			position: fixed;
			display: block;
		}
    `;
	// document.querySelectorAll('.print-ui').style.display = "block"; // only block for now?
	document.head.appendChild(style);
}