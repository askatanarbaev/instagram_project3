from django.shortcuts import get_object_or_404, render, redirect
from .forms import NewCommentForm, NewPostForm, CreateProfileForm
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from django.contrib.auth.decorators import login_required



class PostListView(ListView):
	model = Post
	template_name = 'home.html'
	context_object_name = 'posts'

	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		return context


@login_required
def my_profile(request):
	p = request.user.profile
	user_posts = Post.objects.all()
	return render(request, "profile.html", locals())


class NewProfileView(CreateView, LoginRequiredMixin):
	model = Profile
	template_name = 'create_profile.html'
	form_class = CreateProfileForm
	context_object_name = 'new_profile'

	def form_valid(self, form):
		user = form.save(commit=False)
		user.user = self.request.user
		user.save()
		return redirect('my_profile')


def post_create(request):
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.created_by = request.user
            post.save()
            photo = form.instance
            return redirect('my_profile')
    else:
        form = NewPostForm()
    return render(request, 'post_create.html', locals())


# delete and update

# def edit_profile(request):
#     post = Profile.objects.all()
#     if request == 'POST':
#         form = CreateProfileForm(request.POST, instance=post)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.created_by = request.user
#             post.save()
#             return redirect('home')
#     else:
#         form = CreateProfileForm(instance=post)
#     return render(request, 'edit_profile.html', locals())


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('posts_list')
    return render(request, 'blog/post/post_delete.html', {'post': post})



@login_required
def edit_profile(request):
	if request.method == 'POST':
		p_form = CreateProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if p_form.is_valid():
			p_form.save()
			return redirect('my_profile')
	else:
		p_form = CreateProfileForm(instance=request.user.profile)
	return render(request, 'edit_profile.html', locals())



class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['description', 'image']
	template_name = 'update_post.html'

	def form_valid(self, form):
		form.instance.username = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.created_by:
			return True
		return False


@login_required
def post_delete(request, pk):
	post = Post.objects.get(pk=pk)
	if request.user == post.created_by:
		Post.objects.get(pk=pk).delete()
	return redirect('home')




# work with comments

@login_required
def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	user = request.user
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			data = form.save(commit=False)
			data.post = post
			data.username = user
			data.save()
			return redirect('post-detail', pk=pk)
	else:
		form = NewCommentForm()
	return render(request, 'post_detail.html', locals())

# search

@login_required
def search_posts(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(description__icontains=query)
	return render(request, "search_posts.html", locals())