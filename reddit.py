import os, re, praw, markdown_to_text, time, configparser
from videoscript import VideoScript

redditUrl = "https://www.reddit.com/"

def getContent(outputDir, subreddit) -> VideoScript:
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)

    now = int( time.time() )
    posts = []

    for submission in reddit.subreddit(subreddit).top(time_filter="day", limit=10):
        if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
            continue
        hoursAgoPosted = (now - submission.created_utc) / 3600
        print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
        posts.append(submission)
        break
    return __getContentFromPost(posts[0])

def getContentFromId(outputDir, submissionId) -> VideoScript:
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)
    
    if (submissionId in existingPostIds):
        print("Video already exists!")
        exit()
    try:
        submission = reddit.submission(submissionId)
    except:
        print(f"Submission with id '{submissionId}' not found!")
        exit()
    return __getContentFromPost(submission)

def __getReddit():
    configSecrets = configparser.ConfigParser()
    configSecrets.read('config_secrets.ini')

    return praw.Reddit(
        client_id=configSecrets["Reddit"]["REDDIT_ID"],
        client_secret=configSecrets["Reddit"]["REDDIT_SECRET"],
        # user_agent sounds scary, but it's just a string to identify what your using it for
        # It's common courtesy to use something like <platform>:<name>:<version> by <your name>
        user_agent="Window10:get_top_AMA_posts:v0.1 by u/II_Do2"
    )


def __getContentFromPost(submission) -> VideoScript:
    content = VideoScript(submission.url, submission.title, submission.id)
    print(f"Creating video for post: {submission.title}")
    print(f"Url: {submission.url}")

    failedAttempts = 0
    for comment in submission.comments:
        if(content.addCommentScene(markdown_to_text.markdown_to_text(comment.body), comment.id)):
            failedAttempts += 1
        if (content.canQuickFinish() or (failedAttempts > 2 and content.canBeFinished())):
            break
    return content

def __getExistingPostIds(outputDir):
    files = os.listdir(outputDir)
    # I'm sure anyone knowledgable on python hates this. I had some weird 
    # issues and frankly didn't care to troubleshoot. It works though...
    files = [f for f in files if os.path.isfile(outputDir+'/'+f)]
    return [re.sub(r'.*?-', '', file) for file in files]
