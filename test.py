from weibo import WeiBo


w = WeiBo("15170307370", "lzjlzj123")

pic_id = w.upload_pic("1.jpg")
print(w.original_weibo("成功了ojbk", pic_id=pic_id))
