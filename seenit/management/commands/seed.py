from random import choice, randint
from string import ascii_letters as letters

from django.core.management.base import BaseCommand

from seenit.models import Comment
from seenit.models import Post
from seenit.models import User
from seenit.models import Channel


class Command(BaseCommand):
    help = 'Generates tests data'

    def add_arguments(self, parser):
        parser.add_argument('--thread_count', type=int, default=10)
        parser.add_argument('--root_comments', type=int, default=10)

    def handle(self, *args, **options):
        self.thread_count = options['thread_count']
        self.root_comments = options['root_comments']
        self.random_usernames = [self.get_random_username()
                                 for _ in range(100)]
        for index, _ in enumerate(range(self.thread_count)):
            print("Thread {} out of {}".format(str(index), self.thread_count))
            selftext = self.get_random_sentence()
            title = self.get_random_sentence(max_words=20, max_word_len=10)
            user = self.get_or_create_author(choice(self.random_usernames))
            channel = self.get_or_create_channel()

            post = Post(user=user,
                        title=title,
                        text=selftext,
                        rating=randint(-1000, 1000),
                        channel=channel
                        )
            post.save()

            for _ in range(self.root_comments):
                print("Adding thread comments...")
                comment_author = self.get_or_create_author(
                    choice(self.random_usernames))
                raw_text = self.get_random_sentence(max_words=100)
                new_comment = Comment(user=comment_author, text=raw_text,
                                      rating=randint(-1000, 1000), post=post)
                new_comment.save()
                another_child = choice([True, False])
                while another_child:
                    self.add_replies(new_comment)
                    another_child = choice([True, False])

    def get_or_create_channel(self):
        channel_id = randint(1, 100)
        try:
            channel = Channel.objects.get(pk=channel_id)
            return channel
        except Channel.DoesNotExist:
            print("Creating channel with id{}".format(channel_id))
            new_channel = Channel(name=self.get_random_sentence(
                max_words=5, max_word_len=10))
            new_channel.save()
            return new_channel

    def get_random_username(self, length=6):
        return ''.join(choice(letters) for _ in range(length))

    def get_random_sentence(self, min_words=3, max_words=50,
                            min_word_len=3,
                            max_word_len=15):
        sentence = ''

        for _ in range(0, randint(min_words, max_words)):
            sentence += ''.join(choice(letters)
                                for i in
                                range(randint(min_word_len, max_word_len)))
            sentence += ' '

        return sentence

    def get_or_create_author(self, username):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            print("Creating user {}".format(username))
            new_user = User(username=username, password='greatpassword123',
                            email=f'{username}@test.com')
            new_user.save()
            return new_user

    def add_replies(self, root_comment, depth=1):
        if depth > 5:
            return

        comment_author = self.get_or_create_author(
            choice(self.random_usernames))

        raw_text = self.get_random_sentence()
        new_comment = Comment(user=comment_author, text=raw_text,
                              parent=root_comment, post=root_comment.post,
                              rating=randint(-1000, 1000))
        new_comment.save()
        if choice([True, False]):
            self.add_replies(new_comment, depth + 1)
