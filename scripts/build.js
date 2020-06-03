const matter = require('gray-matter')
const fs = require('fs')
const path = require('path')
const rimraf = require('rimraf')
const handlebars = require('handlebars')
const showdown = require('showdown')
const converter = new showdown.Converter({ tables: true })

const publicPath = path.join(__dirname, '..', 'public')
const templates = {}

handlebars.registerHelper('dateFormat', require('handlebars-dateformat'));

handlebars.registerHelper('getAuthors', function(Authors) {
  return Authors.split(',').map(author => {
    const [_, name, link] = author.trim().match(/^([^<]+)<?([^>]+)?>?$/) || []
    let type = 'url'
    if (link.match(/^[^@]+@[^@]+$/)) {
      type = 'email'
    }
    const authorLink = type === 'email' ? 'mailto:' + link : link
    const authorName = name.trim()

    return ' ' + '<a href="' + authorLink + '" alt="' + authorLink + '">' + authorName + '</a>'
  })
});

handlebars.registerHelper("debug", function(optionalValue) {
  console.log("Current Context");
  console.log("====================");
  console.log(this);

  if (optionalValue) {
    console.log("Value");
    console.log("====================");
    console.log(optionalValue);
  }
});

function getTableOfContents (lines, { children = [], headingType = -1 } = {}) {
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

function loadFrontmatter (filePath) {
  const contents = fs.readFileSync(filePath, { encoding: 'utf8' })
  const parsed = matter(contents)
  parsed.html = converter.makeHtml(parsed.content)
  return parsed
}

function copyAsset (fromPath, toPath) {
  const toPathDirectory = toPath.replace(/^(.*)\/.*?$/, '$1')
  fs.mkdirSync(path.join(publicPath, toPathDirectory), { recursive: true })
  fs.copyFileSync(fromPath, path.join(publicPath, toPath))
}

function renderHTML (uriPath, template, data) {
  const hbTemplate = handlebars.compile(templates[template])
  fs.mkdirSync(path.join(publicPath, uriPath), { recursive: true })
  fs.writeFileSync(path.join(publicPath, uriPath, 'index.html'), hbTemplate(data), { encoding: 'utf8' })
}

const types = { All: [] }

function slugify (string) {
  return string.toLowerCase().replace(/\s/g, '-')
}

function getCipContents (cip) {
  // get all the headings from markdown
  // inside cip.hbs create
}

function build () {
  fs.mkdirSync(publicPath)
  const cipsDirectory = path.join(__dirname, '..')
  const cips = fs.readdirSync(cipsDirectory)
  cips.forEach(item => {
    if (!item.match(/^CIP[\d]{1,}$/)) return
    const assets = fs.readdirSync(path.join(cipsDirectory, item))
    assets.forEach(asset => {
      const assetPath = path.join(cipsDirectory, item, asset)
      if (asset === `${item}.md`) {
        const cip = loadFrontmatter(assetPath)
        cip.tableOfContents = getTableOfContents(cip.content.split('\n'))
        types[cip.data.Type] = types[cip.data.Type] || []
        types[cip.data.Type].push(cip)
        types.All.push(cip)
      } else {
        copyAsset(assetPath, `/cips/${item.toLowerCase()}/${asset}`)
      }
    })
  })

  const headerData = []



  Object.keys(types).forEach(type => {
    headerData.push({ label: type, path: `/${slugify(type)}/` })
  })

  Object.keys(types).forEach(type => {
    
    renderHTML(`/${slugify(type)}/`, 'cips', {
      headerData,
      cips: types[type],
      type,
      title: type
    })

    types[type].forEach(cip => {
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

function clean () {
  rimraf.sync(publicPath)
}

function loadTemplates () {
  const templatedDirectory = path.join(__dirname, '..', 'templates')
  const templateItems = fs.readdirSync(templatedDirectory)
  templateItems.forEach(template => {
    const name = template.replace(/\.hbs$/, '')
    const content = fs.readFileSync(path.join(templatedDirectory, template), { encoding: 'utf8' })
    templates[name] = content
    handlebars.registerPartial(name, content)
  })
}

function copyAssets (relativePath = '') {
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
