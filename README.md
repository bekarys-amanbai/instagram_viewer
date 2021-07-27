# instagram_viewer


### атрибуты
- full_name
- username
- id
- biography
- avatar - ссылка на изображение аватарки
- count_posts - общее количество постов
- url - ссылка на просматриваемую страницу
- last_12_posts - список последних 12 постов, в виде экзмепляра класса InstagramPost

### методы

- get_next_posts(self, count: int = 12) -> list[**InstagramPost**] - возвращает следующий *count* постов (за исключением первых 12, которые находятся в атрибуте last_12_posts)
- get_all_posts(self) -> list[**InstagramPost**] - вернет список из всех постов

## InstagramPost

- is_video: bool
- is_slider: bool
- items: Optional[list[**InstagramPostItems**]]
- url: str
- video_prev: Optional[str]
- datetime: datetime
- post_id: str
- post_url: str
- description: str

## InstagramPostItems:

- is_video: bool
- url: str
- video_prev: str
