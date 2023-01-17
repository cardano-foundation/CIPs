const matter = require('gray-matter')
const fs = require('fs')
const path = require('path')
const rimraf = require('rimraf')
const handlebars = require('handlebars')
const showdown = require('showdown')
const moment = require('moment')
const converter = new showdown.Converter({ tables: true })

const publicPath = path.join(__dirname, '..', 'public')
const templates = {}

handlebars.registerHelper('dateFormat', (d, f) => {
  return moment(d).format(f);
});

handlebars.registerHelper('getAuthors', function (data) {
  if (data.Authors == undefined) {
    throw new Error(`No authors: ${JSON.stringify(data)}`);
  }

  const authors = Array.isArray(data.Authors)
    ? data.Authors
    : data.Authors.split(',');

  return authors.map(author => {
    const [_, name, link] = author.trim().match(/^([^<]+)<?([^>]+)?>?$/) || []
    let type = 'url'
    if (link === undefined) {
      type = 'github'
    } else {
      if (link.match(/^[^@]+@[^@]+$/)) {
        type = 'email'
      }
    }

    const authorLink = type === 'email' ? 'mailto:' + link
      : (type === 'github' ? 'https://github.com/' + name
      : link)
    const authorName = name.trim()

    return ' ' + '<a href="' + authorLink + '" alt="' + authorLink + '">' + authorName + '</a>'
  })
});

handlebars.registerHelper("debug", function (optionalValue) {
  console.log("Current Context");
  console.log("====================");
  console.log(this);

  if (optionalValue) {
    console.log("Value");
    console.log("====================");
    console.log(optionalValue);
  }
});

function getTableOfContents(lines, { children = [], headingType = -1 } = {}) {
  while (lines.length > 0) {
    const line = lines.shift()
    const heading = line.match(/^([#]{1,})\s([^\n]+)$/)
    if (heading) {
      const type = heading[1].length === 1 ? 1 : heading[1].length - 1

      if (type > headingType) {
        const branch = {
          label: heading[2],
          id: heading[2].toLowerCase().replace(/[^a-z0-9]/g, ''),
          type,
          children: getTableOfContents(lines, { children: [], headingType: type })
        }

        children.push(branch)
      } else {
        lines.unshift(line)
        break
      }
    }
  }

  return children
}

function loadFrontmatter(filePath) {
  const raw = fs.readFileSync(filePath, { encoding: 'utf8' })
  const contents = raw
    .replace(/\.\/.*CIP-0*([^\.]+)/g, '/cips/cip$1')
    .replace(/\(\.\/(.*\.md)\)/g, '(./$1.html)')
  const parsed = matter(contents)
  parsed.html = converter.makeHtml(parsed.content)
  return parsed
}

function copyAsset(fromPath, toPath) {
  const toPathDirectory = toPath.replace(/^(.*)\/.*?$/, '$1')
  fs.mkdirSync(path.join(publicPath, toPathDirectory), { recursive: true })
  fs.cpSync(fromPath, path.join(publicPath, toPath), { recursive: true })
}

function renderHTML(uriPath, template, data) {
  const hbTemplate = handlebars.compile(templates[template])
  fs.mkdirSync(path.join(publicPath, uriPath), { recursive: true })
  fs.writeFileSync(path.join(publicPath, uriPath, 'index.html'), hbTemplate(data), { encoding: 'utf8' })
}

const categories = { All: [] }

function slugify(string) {
  return string.toLowerCase().replace(/\s/g, '-')
}

function build() {
  fs.mkdirSync(publicPath)
  const cipsDirectory = path.join(__dirname, '..')
  const cips = fs.readdirSync(cipsDirectory)
  cips.forEach(item => {
    if (!item.match(/^CIP-[\d][\d][\d][\d]{1,}$/)) return
    const assets = fs.readdirSync(path.join(cipsDirectory, item))
    assets.forEach(asset => {
      const assetPath = path.join(cipsDirectory, item, asset)
      if (asset === 'README.md') {
        const cip = loadFrontmatter(assetPath)
        cip.tableOfContents = getTableOfContents(cip.content.split('\n'))
        const category = cip.data.Category || "Unclassified";
        categories[category] = categories[category] || []
        categories[category].push(cip)
        categories.All.push(cip)
      } else {
        const name = item.toLowerCase().replace(/cip-0*([1-9][0-9]*)/g, 'cip$1')
        const title = `${name.replace(/cip/g, 'CIP ')} - Annexe`;
        const cipDir = path.join('cips', name)
        if (asset.endsWith('.md') || asset.endsWith('.markdown')) {
          const absoluteCipDir = path.join(publicPath, cipDir)
          const template = handlebars.compile(templates.annexe)
          const html = converter.makeHtml(fs.readFileSync(assetPath).toString())
          fs.mkdirSync(absoluteCipDir, { recursive: true })
          fs.writeFileSync(
            path.join(absoluteCipDir, asset + '.html'),
            template({ html, title }),
            { encoding: 'utf8' }
          )
        } else {
          copyAsset(assetPath , '/' + path.join(cipDir, asset))
        }
      }
    })
  })

  const headerData = []

  Object.keys(categories).sort((a, b) => {
    if ([a,b].includes("All")) { return a === "All" ? -1 : 1 }
    if ([a,b].includes("Unclassified")) { return a === "Unclassified" ? 1 : -1 }
    return a > b ? 1 : -1;
  }).forEach(category => {
    headerData.push({ label: category, path: `/${slugify(category)}/` })
  })

  Object.keys(categories).forEach(category => {

    renderHTML(`/${slugify(category)}/`, 'cips', {
      headerData,
      cips: categories[category],
      category
    })

    categories[category].forEach(cip => {
      renderHTML(`/cips/cip${cip.data.CIP}/`, 'cip', {
        headerData,
        cip,
        title: cip.Title
      })
    })
  })


  const readme = loadFrontmatter(path.join(__dirname, '..', 'README.md'))
  renderHTML('/', 'home', {
    headerData,
    readme,
    title: 'CIP Cardano Improvement Proposals'
  })
}

function clean() {
  rimraf.sync(publicPath)
}

function loadTemplates() {
  const templatedDirectory = path.join(__dirname, '..', 'templates')
  const templateItems = fs.readdirSync(templatedDirectory)
  templateItems.forEach(template => {
    const name = template.replace(/\.hbs$/, '')
    const content = fs.readFileSync(path.join(templatedDirectory, template), { encoding: 'utf8' })
    templates[name] = content
    handlebars.registerPartial(name, content)
  })
}

function copyAssets(relativePath = '') {
  let assetsDirectory = path.join(__dirname, '..', 'assets')
  if (relativePath) {
    assetsDirectory = path.join(assetsDirectory, relativePath)
    fs.mkdirSync(assetsDirectory, { recursive: true })
  }

  const assets = fs.readdirSync(assetsDirectory)
  assets.forEach(asset => {
    const assetPath = path.join(assetsDirectory, asset)
    if (fs.statSync(assetPath).isDirectory()) {
      copyAssets(path.join(relativePath, asset))
    } else {
      copyAsset(assetPath, path.join('assets', relativePath, asset))
    }
  })
}

clean()
loadTemplates()
build()
copyAssets()
