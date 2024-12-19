from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        con = psycopg2.connect(host="localhost", database="socialMedia", port=5433,
                            user="postgres", password="root", cursor_factory=RealDictCursor)
        cursor = con.cursor()

        print("Connection to database successfull")
        break;

    except Exception as error:
        print("Connection to db failed")
        print("error :", error)
        time.sleep(2)
    

@app.get("/")
def read_root():
    return {"message" : "Welcome to my api"}


# get all the post
@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


# create a new post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(newPost: Post ):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
                   (newPost.title, newPost.content, newPost.published))
    postCreated = cursor.fetchone()
    con.commit()
    return {"data" : postCreated}

# get one post by id

@app.get("/posts/{id}")
def getPost(id: int, respone: Response):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id), ))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"the post with id: {id} not found")

    return {"data": post}


# delete a post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(id: int):
    #  find if the post exist 
    cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id),))
    existedPost = cursor.fetchone()

    if existedPost is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "No post found for this id"})
    
    # starting the deletion
    cursor.execute(""" DELETE FROM posts WHERE id = %s """, (str(id), ))
    con.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# update a post

@app.put("/posts/{id}")
def updatePosts(id: int, post: Post):

    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING * """,
                   (post.title, post.content, post.published, post.rating, str(id), ))
    updatedPost = cursor.fetchone()

    if updatedPost is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "No post found for update"})
    con.commit()

    return {"updated Post": updatedPost}
    