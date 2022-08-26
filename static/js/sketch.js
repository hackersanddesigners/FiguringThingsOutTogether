/**
 * Example P5.js sketch. Puts the page number in back colored letters in 
 * the background. 
 * @param {*} page - current page html node
 * @param {*} num - page number (1 based)
 */

function renderSketch(page, num ){

	const s = (sketch) => {
		let canvas, el;
		let dimensions = {};
		sketch.setup = () => {
			el = page.element;
			dimensions = sketch.getDimensions();
			
			canvas = sketch.createCanvas(el.offsetWidth, el.offsetHeight, sketch.SVG);
			canvas.parent(el);
			canvas.position(0, 0);
			canvas.style("z-index", 0);

			let color = sketch.color(0,0,0)
			sketch.drawNumber(num);
		};

		sketch.drawNumber = (num) => {
			sketch.background(255);
			sketch.fill(sketch.random(255),sketch.random(255),sketch.random(255));
			sketch.textSize(100);
			sketch.text(num, sketch.width/2 - sketch.textWidth(num)/2, sketch.height/2 );

			// Alternatively, convert the sketch to on image and set it as background of the page
			// let dataurl = canvas.canvas.toDataURL('image/png');
			// canvas.parent().style.backgroundImage = dataurl;
			// canvas.style.display = "none";
		}


		/**
		 * Creates an object with the sizes of the document 
		 * margin and bleed on all sides 
		 * @returns Object
		 */
		sketch.getDimensions = () => {
			let dimensions = {}
			dimensions.bleed = sketch.getElementDimensions('bleed');
			dimensions.margin = sketch.getElementDimensions('margin');
			return dimensions;
		}

		/**
		 * Helper function for getDimensions
		 * @param {string} area - part the selector of the document 
		 * @returns Object
		 */
		sketch.getElementDimensions = (area) => {
			let dir = ['top', 'bottom', 'right', 'left'];
			let ret = {};
			for( let i = 0; i < 4; i++) {
				let b = el.querySelector('.pagedjs_' + area + '-' + dir[i]);
				ret[dir[i]] = (i < 2 ) ? b.clientHeight : b.clientWidth;
			}
			return ret;
		}

		// sketch.draw = () => {};
	};

	let myp5 = new p5(s); 
}