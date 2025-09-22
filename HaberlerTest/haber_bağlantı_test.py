import feedparser

# RSS linki
rss_url = "https://www.aa.com.tr/tr/rss/default?cat=guncel"

# RSS verisini çekiyoruz
feed = feedparser.parse(rss_url)

# Haberleri gez
for entry in feed.entries:
    print("Başlık:", entry.title)
    print("Link:", entry.link)
    print("Özet:", entry.summary)
    
    # Görsel kontrolü
    if 'media_content' in entry:
        for media in entry.media_content:
            print("Görsel URL:", media['url'])
    else:
        print("Görsel yok")

    print("-" * 50)
