# Book Starter

[Wiki2Print](https://github.com/hackersanddesigners/wiki2print) allows for inline styling using the CSS button in the editor, but this may get cumbersome in larger projects. This repository is a starting point for creating the styling of a book in a more 'regular' webdevelopment workflow, using Sass, Plumber (for the baseline grid), Gulp for compilation and Browser-sync for live reloading. It is installed as a Flask plugin.

## Getting Started

These instructions will give you a copy of the project up and running on your local machine for development.

### Prerequisites

Requirements for the software and other tools to build
- [Wiki2Print](https://github.com/hackersanddesigners/wiki2print) is installed and running locally.
- [Npm](https://www.npmjs.com/)
- [Gulp](https://gulpjs.com/)

### Installing
This project should be installed as a [plugin](https://pypi.org/project/Flask-Plugin/) to the Flask backend the Wiki2Print is built upon. 
The directory structure should look like this:

```
wiki2print
└── preview
    └── web-interface
         └── plugins
             └── BookStarter
                 ├── __init__.py
                 ├── ...
                 └── plugin.json
```

- Rename the BookStarter directory to be the same as _namespace_ your publication is in with spaces replaces by underscores. (IE, our publication is in Publishing:Making Matters Lexicon, so the plugin in the the directory plugins/Making_Matters_Lexicon.)

- Modify `plugin.json`, set the ID to the _namespace_ as well.

- Install the dependencies
```
npm install
```

- Then start the Gulp default task by running
```
gulp default
```

This will start a webserver running on port 3000 (assuming you have the Wiki2print web-interface running), it proxies the wiki2print server (running on port 5252), but with browsersync included.

### Plumber

https://jamonserrano.github.io/plumber-sass/

TODO: explain why Plumber and how to use it 

### P5.js

TODO: explain why P5.js and how to use it 

- https://p5js.org/
- https://github.com/zenozeng/p5.js-svg


## Authors

There's a lot documentation still missing. Feel free to contact us if you have any questions.
  * **[Heerko van der Kooij](heerko@hackersanddesigners.nl)**
  * **[Karl Moubarak](karl@hackersanddesigners.nl)**

## License
Wiki2Print and this template are both licensed under the [CC4r](https://constantvzw.org/wefts/cc4r.en.html) license.

## Acknowledgments  
  - See the wiki2print readme for credits for the wonderful projects that wiki2print builds upon. 
  - Billie Thompson - Provided README Template - [PurpleBooth](https://github.com/PurpleBooth)
  - TODO: add font credits