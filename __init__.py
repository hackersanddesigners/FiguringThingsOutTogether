"""BookStarter Flask plugin
This Flask plugin overwrites some of the default 
routes of Wiki2print so we can customize the output. 
We're loading a custom html template, filter some 
of the output from Mediawiki to allow for things
like image spreads, and to filter out some unwanted 
html. Depending on taste some of the filtering could
be moved to javascript in paged_custom.js
Further documentation:
https://flask.palletsprojects.com/en/2.1.x/
and the flask_plugin docs:
https://github.com/flask-plugin/flask-plugin
"""

from pprint import pprint
import flask
from flask import request
from flask_plugin import Plugin
from api import *
from bs4 import BeautifulSoup
import re, copy, sys, os, glob
# import config

sys.path.insert(0, '.../../..')
from config import config as conf

WIKI         = conf['wiki']['base_url']
SUBJECT_NS   = conf['wiki']['subject_ns']
STYLES_NS    = conf['wiki']['styles_ns']

plugin = Plugin(
  static_folder='static',
  template_folder='templates'
)

# Endpoint for the plugin for getting the rendered publication
# path: /plugin/<plugin-name>/pdf/<publication-name>
# plugin & application name are probably the same
# this overwrites the default /pdf route

@plugin.route('/pdf/<string:pagename>', methods=['GET', 'POST'])
def pagedjs(pagename):	
  publication = get_publication(
    WIKI,
    SUBJECT_NS,
    STYLES_NS,
    pagename,
  )
  return filter(flask.render_template(
    'custom.html', 
    title = pagename,
    html  = publication['html'],
  ))

@plugin.route('/html/', methods=['GET', 'POST'])
def inspect():
  # from pprint import pprint
  # pprint(vars(plugin.name))

  publication = get_publication(
    WIKI,
    SUBJECT_NS,
    STYLES_NS,
    plugin.name,
  )
  return web_filter(flask.render_template(
    'web-view.html', 
    title = plugin.name,
    html  = publication['html'],
    css   = publication['css']
  ))

# The filters in this plugin work on request time
# this endpoint returns the filtered html, 
# Theres no link in the UI to get to it.
# path: /plugin/<plugin-name>/html_filtered/<publication-name>

@plugin.route('/html_filtered/<string:pagename>', methods=['GET', 'POST'])
def filtered_html(pagename):
  publication = get_publication(
    WIKI,
    SUBJECT_NS,
    STYLES_NS,
    pagename,
  )
  return web_filter(flask.render_template(
    'inspect.html', 
    title = pagename,
    html  = publication['html'],
    css   = publication['css']
  ))

# misc transformations of the mediawiki html
def filter(html):
  print("filtering...")	
  soup = BeautifulSoup(html, 'html.parser')
  soup = fixImageLinks(soup)
  soup = imageSpreads(soup)
  # soup = wrapChapters(soup)
  soup = wrapAuthors(soup)
  soup = wrapTitleImages(soup)
  soup = filterPBR(soup)
  soup = hideFromBook(soup)
  soup = tocID(soup)
  soup = internalLinks(soup)
  html = str(soup) #soup.prettify() # dont use prettify. It causes whitespace in layout in some instances #
  html = removeSrcSets(html)
  return html

def web_filter(html):
  soup = BeautifulSoup(html, 'html.parser')
  soup = fixImageLinks(soup)
  soup = moveToc(soup)
  soup = scriptothek(soup)
  html = str(soup)
  html = removeSrcSets(html)
  return html

def scriptothek(soup):
  content = soup.select('.content')
  # search for nodes with class scriptothek
  # els = soup.select('.scriptothek')
  els = soup.select('img.scriptothek, .scriptothek img')
  last_id = ""
  cnt = 0
  # create initial elements
  scriptothek = soup.new_tag('div', **{"class": 'scriptothek-wrapper'})
  container = soup.new_tag('div')
  slideshow = soup.new_tag('div', **{"class":"scriptothek-slideshow scriptothek-slideshow-"+ str(cnt) , "data-slideshow": cnt})
  container.append(slideshow)
  for el in els:
    # try to find chapter
    article = el.find_parent('div', class_="article")
    id = article['id']
    # print(el.prettify())
    if( id != last_id ):
      # if new chapter, new div. Append the old div if it has content
      # print("---------------------")
      # # print(len(container.contents))
      # print(container.prettify())
      # print("---------------------")
      # if( len(container.contents) > 1 ):
        # print(container.prettify())
      container["class"] = 'scriptothek-chapter scriptothek-chapter-' + str(cnt) + ' chapter-' + last_id
      container["data-slideshow"] = cnt
      scriptothek.append(container)
      cnt += 1
      # create elements for next chapter
      container = soup.new_tag('div')
      slideshow = soup.new_tag('div', **{"class":"scriptothek-slideshow scriptothek-slideshow-"+ str(cnt), "data-slideshow": cnt})
      container.append(slideshow)
      last_id = id

    if("title_image" in el['class']):
      # directly add to scriptothek
      thumb = el.find_parent(class_="thumb")
      el.parent["class"] += ["script-trailer", "script-trailer-" + str( cnt ) ]
      el.parent["data-slideshow"] = cnt
      del el["srcset"]
      container.insert(0, el.parent)
      thumb.decompose() #remove the surrounding html
    else:
      el["class"] += ["script-image", "script-image-" + str( cnt ) ]
      del el["srcset"]
      el["data-slideshow"] = cnt
      # print(el)
      slideshow.append(el.parent)
  # print(scriptothek.prettify())
  content[0].insert_after(scriptothek)
  return soup

# def getArticleTitle(article):
#   title = ""
#   h3 = article.find(h3)
#   title = h3.span.string
#   return title
  
# adds a title attribute to internal links with the name of the article that is being linked to.
def internalLinks(soup):
  links = soup.select('a[href^="#"]:not(#toc-list *, [class^="toclevel-"] *, .print-ui *):not(.footnote)')
  for link in links:
    href = link['href']
    print( "looking for article " + href)
    ref = soup.find(id=href[1:])
    if( ref ):
      # should be a div, but i've also seen the headline>span
      if( ref.name == "span" ):
        txt = ref.string
      elif( ref.name == "div" ):
        txt = ''.join(ref.h3.find_all(text=True, recursive=True))
      else:
        txt = "No title found."
      print("Found article. Title: " + txt )
      link['title'] = txt
      link['class'] = "internal-link"
  return soup

def extractText(element):
  string = ""
  
  return string

def hideFromBook(soup):
  hide = soup.find_all(class_="hide-from-book")
  for el in hide:
    el.decompose()
  return soup

def fixImageLinks(soup):
  images = soup.find_all("img")
  for image in images:
    parent = image.parent
    if( parent.name == "a"):
      parent['href'] = image['src']
  return soup

def tocID(soup):
  toc = soup.select('.chapter:first-of-type [class^="toclimit-"] > div > ul')
  if( toc ):
    toc[0]['id'] = "toc-list"
  return soup
  
def moveToc(soup):
  toc_wrap = soup.new_tag('div', **{"class": 'toc-wrap'}) 
  toc_css = soup.select('.chapter:first-of-type style[data-mw-deduplicate]')
  toc = soup.select('.chapter:first-of-type [class^="toclimit-"]')
  content = soup.select('.content')
  if( toc_css and toc and content ):
    toc_wrap.append(toc_css[0])
    toc_wrap.append(toc[0])
    content[0].insert_before(toc_wrap)
  return soup
  
#filters out br's wrapped in p's without other content
def filterPBR(soup):
  ps = soup.select('p:has(br:first-child)')
  for p in ps:
    if(len(p.contents) == 2 and p.string == None and len(p.contents[1]) == 1 ):
      br = soup.new_tag('br', **{"class": 'replaced'}) 
      p.replace_with(br)
  return soup

# wrap author span in a div to have some control over the layout
def wrapAuthors(soup):
  authors = soup.find_all("span", class_="author") 
  for author in authors:
    div = soup.new_tag('div', **{"class": 'author-wrap'}) 
    div.append(copy.copy(author))
    author.replace_with(div)
  return soup

# wrap author span in a div to have some control over the layout
def wrapTitleImages(soup):
  # images = soup.find_all("img", class_="title_image") 
  images = soup.select('img.title_image,img.wide_image')
  for image in images:
    # bg = soup.new_tag('span', **{"class": 'bg'})
    # image.wrap(bg)
    wrap = image.find_parent("div", class_="thumb")
    wrap['class'] = wrap.get('class', []) + ['title-image-wrap']
    if('title_image' in  image.attrs['class']):
      # find the chapter title?
      article = image.find_parent('div', class_="article")
      h3 = article.find('h3')
      # create element to set margin content string
      title = soup.new_tag('div', **{"class": 'article-title'})
      clone = copy.copy(h3)
      clone.name = 'div'
      title.append(clone)
      # insert it before the wrap
      wrap.insert(0,title)
    # image.parent['class'] = image.parent.get('class', []) + ['bg'] # add bg class for showing/hiding fore/background
  return soup

# Searches in the document for h2 tags and author divs (immediatly following an h2!)
# All content besides those two get wrapped in a <div class="article-contents"> 
def wrapChapters(soup):
  chapter_name = ""
  last_tag_was_h2 = False
  
  main = soup.find("div", class_="mw-parser-output")
  new_main = soup.new_tag('div', **{"class": 'mw-parser-output wrapped'}) 
  article = soup.new_tag('div', **{"class": 'article-wrap ' + chapter_name}) 
  contents = soup.new_tag('div', **{"class": 'article-contents ' + chapter_name}) 
  children = iter(main.children)
  
  for child in children:
    if( last_tag_was_h2 ): # check if element immediately after h2 has a author div.
      if(child.name == None): # only tags
        continue
      auth = child.find_all(class_="author") 
      if len( auth ) > 0:
        article.append(copy.copy(auth[0])) # append it to the doc
        last_tag_was_h2 = False
        next(children)
        continue # next element in the loop
      
    if(child.name == 'h2'):
      chapter_name = re.sub('\W+','-', child.find(text=True).lower())
      
      article.append(copy.copy(contents)) #existing content goes in previous article
      article = soup.new_tag('div', **{"class": 'article-wrap ' + chapter_name})  # new article 
      article.append(copy.copy(child)) #append the h2
      new_main.append(article) #h2
      # new_main.append(copy.copy(contents)) # append the previous content tag. TODO: don't do this if contents is empty :)
      # new_main.append(copy.copy(child)) # append the h2 element as well
      contents = soup.new_tag('div', **{"class": 'article-contents ' + chapter_name}) # new contents element for next chapter
      
      chapter_name = ""
      last_tag_was_h2 = True
    else:
      contents.append(copy.copy(child))
      
  new_main.append(contents) # append the previous content tag. TODO: don't do this if contents is empty :)
  main.replace_with(new_main) # replace with the new structure
  
  return soup 

# somethings wrong with the srcsets from the wiki. We only need originals anyway.
def removeSrcSets(html):
  """
    html = string (HTML)
  """
  html = re.sub(r"srcset=", "xsrcset=", html)
  return html


# Creates the html necessary for spreads
# <section class="full-spread-image-section">
# 	<div class="full-page-image full-page-image-left">
# 		<div>
# 			<img src="src" />
# 		</div>
# 	</div>
# 	<div class="full-page-image">
# 		<div>
# 			<img src="src" />
# 		</div>
# 	</div>
# </section>

def createSpreadSection(soup, img):
  section = soup.new_tag('section', **{"class": 'full-spread-image-section'}) # outer section
  fpi = soup.new_tag('div', **{"class":'full-page-image full-page-image-left'}) # outer wrapper for image
  div = soup.new_tag('div') # inner wrapper for image
  if( img ):
    div.append(img) # image in inner div
  else:
    print( "missing image for spread?	")
  fpi.append(div) # div in outer wrapper
  section.append(fpi) # wrapper in section
  fpi2 = copy.copy(fpi)  # copied
  fpi2['class'] = "full-page-image full-page-image-right"
  section.append(fpi2)
  return section

# Finds span.spread in the HTML content and replaces
# them with the spread appropriate html structure
def imageSpreads(soup):
  spreads = soup.find_all(class_='spread')
  if( spreads ):
    for spread in spreads:
      img = spread.find("img")
      if( not img ):
        print( "missing image for spread?	", spread)
      else:
        section = createSpreadSection(soup, img)
        caption = spread.find(class_='thumbcaption')
        if(caption): # is thumbnail, check for caption
          if( len(caption.contents) > 1):
            to_remove = caption.find(class_='magnify')
            to_remove.extract()
            caption['class'] = 'full-spread-image-caption'
            section.div.next_sibling.append(caption) # append the caption to the right page
      spread.replace_with(section)
      if(section.next_sibling and section.next_sibling.name == 'p'):
        p = section.next_sibling
        if len(p.get_text(strip=True)) == 0:
          p.extract() # Remove empty tag
  return soup