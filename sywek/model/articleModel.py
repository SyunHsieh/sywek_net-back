from ..Article import Article


def searchArticleByUser(searchStr, searchTag, searchCount, searchOffset):
    """
    Return articles' info when match the searchRules
    Return None when not match.
    """

    _ret = Article.searchArticle(
        searchStr, searchTag, searchCount, searchOffset)

    return [{'id': art.id, 'isOpened': art.isOpened,
             'articleHeader': art.header, 'secondHeader': art.secondHeader, 'headerImage': art.headerImage, 'postDT': art.postDT, 'lastEditDT': art.lastEditDT, 'authorInfo': {'authorName': art.author.name, 'authorId': art.author.id}} for art in _ret]


def fetchArticleJsonAndInfo(articleId):
    """
    Return false when fetch article failed (article not exists which article has articleId)
    Return true when fetch article successed
    Return format => (flag , articleRef)
    articleRef{
        'articleId' : article's id,
        'articleJsonifyFunc' :article parse to json function's address,
        'articleStatus' : boolean > is article publish
    }
    """

    _article = Article(articleId)

    if _article is None or not _article.isSearchingInDB:
        return (False, None)

    _articleRef = {
        'articleId': _article.id,
        'articleStatus': _article.isOpened,
        'articleJsonifyFunc': _article.jsonify
    }
    return (True, _articleRef)
