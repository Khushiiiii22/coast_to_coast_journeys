const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('/Users/priyeshsrivastava/Travel production/templates/index.html', 'utf8');

process.on('unhandledRejection', (reason, promise) => {
  console.log('Unhandled Rejection at:', reason.stack || reason)
})

const virtualConsole = new jsdom.VirtualConsole();
virtualConsole.on("error", (e) => { console.error("JSDOM Error:", e.stack || e); });
virtualConsole.on("jsdomError", (e) => { console.error("JSDOM jsdomError:", e.stack || e); });
virtualConsole.on("log", (m) => { console.log("JSDOM Log:", m); });

try {
    const dom = new JSDOM(html, { runScripts: "dangerously", virtualConsole });
} catch(e) {
    console.log(e);
}
