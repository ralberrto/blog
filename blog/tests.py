from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Post
from django.urls import reverse


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="password",
        )

        cls.post = Post.objects.create(
            title="Some Title",
            body="Some Content",
            author=cls.user,
        )

    def test_post_model(self):
        self.assertEqual(self.post.title, "Some Title")
        self.assertEqual(self.post.body, "Some Content")
        self.assertEqual(self.post.author.username, "testuser")
        self.assertEqual(str(self.post.title), "Some Title")
        self.assertEqual(self.post.get_absolute_url(), "/post/1/")

    def test_resource_exist_in_location_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_resource_exist_in_location_post(self):
        response = self.client.get("/post/1/")
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "<p>Some Content</p>")

    def test_post(self):
        response = self.client.get(reverse("post_detail", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        no_response = self.client.get("/post/10/")
        self.assertEqual(no_response.status_code, 404)
        self.assertTemplateUsed(response, "post_detail.html")
        self.assertTemplateNotUsed(no_response, "post_detail.html")
        self.assertContains(response, "<h2>Some Title</h2>")

    def test_post_createview(self):
        response = self.client.post(
            reverse("post_new"),
            {
                "title": "new title",
                "author": self.user.id,
                "body": "new body",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.last().title, "new title")
        self.assertEqual(Post.objects.last().body, "new body")

    def test_post_updateview(self):
        response = self.client.post(
            reverse("post_edit", args="1"),
            {
                "title": "modified title",
                "body": "new body",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.last().title, "modified title")
        self.assertEqual(Post.objects.last().body, "new body")

    def test_post_deleteview(self):
        response = self.client.post(reverse("post_delete", args="1"))
        self.assertEqual(response.status_code, 302)
