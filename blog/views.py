from multiprocessing import get_context
from django.shortcuts import render,  redirect
from django.views.generic import View, TemplateView, CreateView
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms
from django.urls import reverse

#TopページのIndexページのview
class IndexView(View):
    #このviewがコールされたら最初にget関数が呼ばれる
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.order_by('-id') #新しいものから順番に並べる
        return render(request, 'blog/index.html',{
            'post_data': post_data
        })

#記事詳細画面のview
class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk']) #pkで記事を特定してデータ取得
        return render(request, 'blog/post_detail.html',{
            'post_data': post_data
        })

#記事投稿のview
class CreatePostView(LoginRequiredMixin, CreateView):
    template_name = 'blog/post_form.html'
    form_class = PostForm

    def get_success_url(self): 
        return reverse("index") #入力フォーム内容がセーブできた時の遷移先

    def get_context_data(self, **kwargs):
        ctx=super().get_context_data(**kwargs) #オーバーライド前のget_context_dataで返されるオブジェクトを格納

        if self.request.method=="POST": #"POST"が呼び出されたときの処理
            post_formset = self.request.POST.copy() #request.POSTをコピーして変数に格納
            files = self.request.FILES  #FILESを変数に格納
            post_formset['contentcard-TOTAL_FORMS']=1 #フォームの数 formsetを使う場合必須
            post_formset['contentcard-INITIAL_FORMS']=0 #formsetを使う場合必須
            ctx["blog_formset"] = CardFormset(post_formset, files) #変数をフォームセットに渡す
        else:
            ctx["blog_formset"] = CardFormset()

        return ctx
   

    def form_valid(self, form):
        ctx = self.get_context_data()
        blog_formset = ctx["blog_formset"]

        if blog_formset.is_valid():
            self.object=form.save(commit=False)
            self.object.author=self.request.user
            self.object.save()
            blog_formset.instance = self.object
            blog_formset.save()
            return redirect(self.get_success_url())

        else:
            ctx["form"] = form
            return self.render_to_response(ctx)



#編集画面のview
class PostEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        form = PostForm(
            request.POST or None,
            initial = {
                'title' : post_data.title,
                'category' : post_data.category,
                'content' : post_data.content,
                'image' : post_data.image
            }
        )
        
        return render(request, 'blog/post_form.html',{
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            post_data = Post.objects.get(id=self.kwargs['pk'])
            post_data.title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            category_data = Category.objects.get(name=category)
            post_data.category = category_data
            post_data.content = form.cleaned_data['content']
           
            if request.FILES:
                post_data.image = request.FILES.get('image')
            post_data.save()
            return redirect('post_detail', self.kwargs['pk'])


        return render(request, 'blog/post_form.html',{
            'form': form
        })

#投稿削除のview
class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'blog/post_delete.html',{
            'post_data': post_data
        })

    def post(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        post_data.delete()
        return redirect('index')

#カテゴリごとに記事をまとめたview
class CategoryView(View):
    def get(self, request, *args, **kwargs):
        category_data = Category.objects.get(
            name=self.kwargs['category'])
        post_data = Post.objects.order_by('-id').filter(
            category=category_data)
        return render(request, 'blog/index.html', {
            'post_data' : post_data
        })


# ___ここから下はお試し用____

class TestDetailView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'test_detail.html',{
            'post_data': post_data
        })

class BlogTestView(TemplateView):
    template_name = "test.html"

    def get(self, request, *args, **kwargs):
        post_data = Post.objects.order_by('-id')
        return render(request, 'test.html',{
            'post_data': post_data
        })




